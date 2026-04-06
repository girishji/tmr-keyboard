# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# KiCad Python script to draw tracks on the switch footprint
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew
import math
from pcbnew import VECTOR2I, FromMM

board = pcbnew.GetBoard()
SWITCH_COUNT = 72
KEY_SPACING = 19.00  # Standard key spacing in mm

# Retrieve footprints. Indices 0 are unused/dummy.
switches = [board.FindFootprintByReference(f'S{i}') for i in range(SWITCH_COUNT + 1)]


def mm_to_nm(mm_val):
    """Converts millimeters to KiCad internal units (nanometers)."""
    return pcbnew.FromMM(mm_val)


def intersect(P, A, Q, B):
    """Return intersection point of two directed line segments."""
    # Based on:
    # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
    R, S = (A - P, B - Q)
    rs = R.Cross(S)
    assert rs != 0, 'Lines maybe parallel or one of the points is the intersection'
    t = (Q - P).Cross(S) / rs
    return P + R.Resize(int(R.EuclideanNorm() * t))


def rotate(V, theta):
    """Rotate a vector by angle theta."""
    sin, cos = (math.sin(math.radians(theta)), math.cos(math.radians(theta)))
    return VECTOR2I(int(cos * V.x - sin * V.y), int(sin * V.x + cos * V.y))


def draw_track(R, S, net_name, width=mm_to_nm(0.2)):
    """Draw a track from R to S."""
    layer = pcbnew.B_Cu
    net_code = board.GetNetcodeFromNetname(net_name)
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(R)
    track.SetEnd(S)
    track.SetWidth(width)
    track.SetLayer(layer)
    track.SetNetCode(net_code)
    board.Add(track)


def draw_via(P, net_name="GND"):
    """Draw via at point P. net_name is the net to connect via to."""
    net_code = board.GetNetcodeFromNetname(net_name)

    # Create the VIA object
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(P)
    via.SetDrill(mm_to_nm(0.3))
    via.SetWidth(mm_to_nm(0.6))

    # Set the layer span
    via.SetTopLayer(pcbnew.F_Cu)
    via.SetBottomLayer(pcbnew.B_Cu)

    # Assign the net code. This is crucial for the via to properly connect
    # tracks and plane fills
    via.SetNetCode(net_code)
    board.Add(via)


def is_equal_with_tolerance(point1, point2):
    """Compare two VECTOR2I points with tolerance."""
    TOLERANCE_IU = 100
    if abs(point1.x - point2.x) <= TOLERANCE_IU and abs(point1.y - point2.y) <= TOLERANCE_IU:
         return True
    return False


def remove_track(A, B):
    """Remove track between points A and B."""
    tracks = list(board.GetTracks())
    for track in tracks:
        if isinstance(track, pcbnew.PCB_TRACK):
            start_pos = track.GetStart()
            end_pos = track.GetEnd()
            # Start is A and End is B
            match_A_to_B = (is_equal_with_tolerance(start_pos, A) and
                            is_equal_with_tolerance(end_pos, B))
            # Start is B and End is A
            match_B_to_A = (is_equal_with_tolerance(start_pos, B) and
                            is_equal_with_tolerance(end_pos, A))
            if match_A_to_B or match_B_to_A:
                board.Remove(track)


def remove_via(A):
    """Remove via at point A."""
    items = list(board.GetDrawings())
    for via in items:
        if isinstance(via, pcbnew.PCB_VIA):
            via_pos = via.GetPosition()
            if is_equal_with_tolerance(via_pos, A, TOLERANCE_IU):
                board.Remove(via)


def draw_switch_tracks(idx):
    e = mm_to_nm(0.1)
    angle = -switches[idx].GetOrientationDegrees()
    cvout = board.FindFootprintByReference(f'Cvout{idx}')
    pads = list(cvout.Pads())
    C1, C2a, C2b, C2c = [pads[i].GetPosition() for i in range(4)]

    tmr = board.FindFootprintByReference(f'TMR{idx}')
    pads = list(tmr.Pads())
    T1, T2, T3, T4 = [pads[i].GetPosition() for i in range(4)]

    net = pads[0].GetNetname()
    draw_intersecting_tracks(C1, C1 + rotate(VECTOR2I(e, 0), -45 + angle), T1, T1 + rotate(VECTOR2I(-e, 0), angle), net)

    net = pads[1].GetNetname()
    draw_intersecting_tracks(T2, T2 + rotate(VECTOR2I(-e, 0), 45 + angle), C2c, C2c + rotate(VECTOR2I(e, 0), angle), net)

    draw_intersecting_tracks(T2, T2 + rotate(VECTOR2I(-e, 0), -45 + angle), T4, T4 + rotate(VECTOR2I(0, -e), angle), net)

    cvout = board.FindFootprintByReference(f'Cvcc{idx}')
    pads = list(cvout.Pads())
    C1, C2 = [pads[i].GetPosition() for i in range(2)]
    net = pads[0].GetNetname()
    remove_track(C1, T3)
    draw_track(C1, T3, net, mm_to_nm(0.25))

    A = T4 + VECTOR2I(-mm_to_nm(0.65), 0)
    remove_track(A, T4)
    draw_track(A, T4, net)
    net = pads[1].GetNetname()
    draw_intersecting_tracks(A, A + rotate(VECTOR2I(-e, 0), -45 + angle), C2, C2 + rotate(VECTOR2I(0, -e), angle), net)


def draw_intersecting_tracks(A, B, C, D, net):
    """Draw tracks between directed line segments AB and CD."""
    I = intersect(A, B, C, D)
    remove_track(A, I)
    remove_track(I, C)
    draw_track(A, I, net)
    draw_track(I, C, net)


def draw_angled_tracks():
    """Draw tracks needed for rotated switches in last row."""
    EPSILON = VECTOR2I(mm_to_nm(0.1), 0)  # Very small line segment

    def draw_angled_tracks_inner(tmr, btm_clearance, side_clearance, left):
        deg = tmr.GetOrientationDegrees()
        pads = list(tmr.Pads())
        A = pads[1].GetPosition()
        B = A + rotate(EPSILON, -deg + (45 if left else 135))
        net = pads[1].GetNetname()
        if left:
            deg2 = switches[64].GetOrientationDegrees()
            C = switches[64].GetPosition()
            x_offset = mm_to_nm(6 - side_clearance)
        else:
            deg2 = switches[66].GetOrientationDegrees()
            C = switches[66].GetPosition()
            x_offset = -mm_to_nm(6 - side_clearance)
        C = C + rotate(VECTOR2I(x_offset, mm_to_nm(KEY_SPACING / 2 - btm_clearance)), -deg2)
        D = C + rotate(EPSILON, -deg2 + (180 if left else 0))
        draw_intersecting_tracks(A, B, C, D, net)

        A = C
        B = A + rotate(EPSILON, -deg2 - (45 if left else 135))
        if left:
            C = switches[64].GetPosition() \
                + rotate(VECTOR2I(mm_to_nm(KEY_SPACING / 2 - side_clearance),
                                  -mm_to_nm(KEY_SPACING - 3)), -deg2)
        else:
            C = switches[66].GetPosition() \
                + rotate(VECTOR2I(-mm_to_nm(KEY_SPACING / 2 - side_clearance),
                                  -mm_to_nm(KEY_SPACING - 3)), -deg2)
        D = C + rotate(EPSILON, -deg2 + 90)
        draw_intersecting_tracks(A, B, C, D, net)

    tmrfp = board.FindFootprintByReference('TMR62')
    draw_angled_tracks_inner(tmrfp, 1.5, 1, True)
    tmrfp = board.FindFootprintByReference('TMR63')
    draw_angled_tracks_inner(tmrfp, 2, 1.5, True)
    tmrfp = board.FindFootprintByReference('TMR64')
    draw_angled_tracks_inner(tmrfp, 2.5, 2, True)

    tmrfp = board.FindFootprintByReference('TMR68')
    draw_angled_tracks_inner(tmrfp, 1.5, 1, False)
    tmrfp = board.FindFootprintByReference('TMR67')
    draw_angled_tracks_inner(tmrfp, 2, 1.5, False)
    tmrfp = board.FindFootprintByReference('TMR66')
    draw_angled_tracks_inner(tmrfp, 2.5, 2, False)


def main():
    EXCLUDE = []

    for i in range(1, SWITCH_COUNT + 1):
        if switches[i] and not i in EXCLUDE:
            draw_switch_tracks(i)

    pcbnew.Refresh()


main()
