# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place footprints
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

from enum import Enum
import math
import pcbnew
from pcbnew import VECTOR2I

Layer = pcbnew.Edge_Cuts

dim = 19.00
COUNT = 72
board = pcbnew.GetBoard()

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]


def draw_line(start, end):
    board = pcbnew.GetBoard()
    ls = pcbnew.PCB_SHAPE(board)
    ls.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ls.SetStart(start)
    ls.SetEnd(end)
    ls.SetLayer(Layer)
    # ls.SetWidth(int(0.12 * pcbnew.IU_PER_MM))
    board.Add(ls)


def draw_arc(start, mid, end):
    board = pcbnew.GetBoard()
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetArcGeometry(start, mid, end)
    arc.SetLayer(Layer)
    board.Add(arc)


# Resources:
# https://www.nagwa.com/en/explainers/606170705790/
# https://www.nagwa.com/en/explainers/578165351487/
# Learn about unit vectors, expressing vector A in terms of B and C, intersection point,
# dot product, cross product, etc.
# https://www.nagwa.com/en/explainers/762143183130/
# A vector is an object that has a magnitude and a direction.
# A Vector is expressed as (x, y) in terms of unit vectors along x, y.
# Directed line segments are written as ((x1, y1), (x2, y2)).

# Based on:
# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
def intersect(P, A, Q, B):
    """Return intersection point of two directed line segments."""
    R, S = (A - P, B - Q)
    rs = R.Cross(S)
    assert rs != 0, 'Lines maybe parallel or one of the points is the intersection'
    t = (Q - P).Cross(S) / rs
    return P + R.Resize(int(R.EuclideanNorm() * t))


def arc(A, B, C, D, radius):
    """Return begin, mid, and end points of arc."""
    I = intersect(A, B, C, D)
    AB, CD = (B - A, D - C)
    iangle = math.acos(AB.Dot(CD) / (AB.EuclideanNorm() * CD.EuclideanNorm())) # intersection angle
    norm_EabI = int(radius / math.tan(iangle / 2)) # length of segment from intersection to end pt
    BEab = AB.Resize((I - A).EuclideanNorm() - AB.EuclideanNorm() - norm_EabI) # AI = I - A
    Eab = B + BEab
    BEcd = CD.Resize((I - C).EuclideanNorm() - CD.EuclideanNorm() - norm_EabI)
    Ecd = D + BEcd
    M = (Eab + Ecd) / 2
    MI = I - M
    norm_OI = math.sqrt(norm_EabI ** 2 + radius ** 2) # O is the center of rounding circle
    MarcI = MI.Resize(int(norm_OI - radius))
    Marc = I - MarcI
    return (Eab, Marc, Ecd)


def draw_arc_fill_lines(AB, CD, radius):
    """Draw rounded arc between directed line segments AB and CD and extend lines."""
    A, B, C, D = *AB, *CD
    Eab, Marc, Ecd = arc(A, B, C, D, radius)
    draw_line(A, B)
    draw_line(B, Eab)
    draw_line(C, D)
    draw_line(D, Ecd)
    draw_arc(Eab, Marc, Ecd)


def rotate(V, theta):
    """Rotate a vector by angle theta."""
    sin, cos = (math.sin(math.radians(theta)), math.cos(math.radians(theta)))
    return VECTOR2I(int(cos * V.x - sin * V.y), int(sin * V.x + cos * V.y))


mil = lambda x: int(x * 1e6)

# Create directed line segment from vector X. 'left' is vector (-delta, 0),
# etc. Helps with starting and ending arc. 'X' is a directed line segment
# represented by (x, y).
arc_dls = mil(0.1) # Length of very small directed line segment after the arc
left = lambda X, angle=0: (X, X + rotate(VECTOR2I(-arc_dls, 0), angle))
right = lambda X, angle=0: (X, X + rotate(VECTOR2I(arc_dls, 0), angle))
up = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, -arc_dls), angle))
down = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, arc_dls), angle))

radius = mil(1)
radius_half = mil(0.5)
radius_wrist_rest = mil(10)

dls = 2 * arc_dls # Length from where directed line segment is specified
wrist = {'xoffset': mil(64), 'yoffset': mil(28), 'width': mil(88), 'height': mil(65)}

holes = [board.FindFootprintByReference('H' + str(i)) for i in range(9)]
hole_count  = sum(h is not None for h in holes)

half = mil(dim / 2)
# offset = mil(0.1)
# offset = mil(0.0)
offset = -mil(0.1)


def place_hole(A, B, C, D):
    """Place mounting hole."""
    I = intersect(A, B, C, D)
    if holes[place_hole.idx]:
        AB, CD = (B - A, D - C)
        offset = radius - mil(4.0)
        holes[place_hole.idx].SetPosition(I - AB.Resize(offset) - CD.Resize(offset))
        place_hole.idx += 1
place_hole.idx = 1


def draw_wrist(L):
    """Draw wrist and place it at vector L."""
    radius = radius_wrist_rest
    R = L
    S = VECTOR2I(R) + VECTOR2I(-radius - dls, wrist['height'] - dls - radius)
    draw_arc_fill_lines(left(R), up(S), radius)
    place_hole(*left(R), *up(S))
    R = VECTOR2I(S)
    S += VECTOR2I(radius + dls, radius + dls)
    draw_arc_fill_lines(down(R), left(S), radius)
    place_hole(*down(R), *left(S))
    R = VECTOR2I(S)
    S += VECTOR2I(wrist['width'] - radius - dls, -radius - dls)
    draw_arc_fill_lines(right(R), down(S), radius)
    place_hole(*right(R), *down(S))
    R = VECTOR2I(S)
    S += VECTOR2I(-radius - dls, -wrist['height'] + radius + dls)
    draw_arc_fill_lines(up(R), right(S), radius)
    place_hole(*up(R), *right(S))

    # Cutout
    thickness = mil(11)
    cradius = mil(6)
    R = L + VECTOR2I(int(wrist['width'] / 2) - radius - dls, thickness)
    S = R + VECTOR2I(-int(wrist['width'] / 2) + thickness, int(wrist['height'] / 2) - thickness)
    draw_arc_fill_lines(left(R), up(S), cradius)
    R = VECTOR2I(S)
    S += VECTOR2I(int(wrist['width'] / 2) - thickness, int(wrist['height'] / 2) - thickness)
    draw_arc_fill_lines(down(R), left(S), cradius)
    R = VECTOR2I(S)
    S += VECTOR2I(int(wrist['width'] / 2) - thickness, -int(wrist['height'] / 2) + thickness)
    draw_arc_fill_lines(right(R), down(S), cradius)
    R = VECTOR2I(S)
    S = L + VECTOR2I(int(wrist['width'] / 2) - radius - dls, thickness)
    draw_arc_fill_lines(up(R), right(S), cradius)


def draw_wristrest():
    # Left side
    R = switches[65].GetPosition() + VECTOR2I(0, half + offset)
    angle = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(half + offset, 0), angle)
    draw_arc_fill_lines(left(R), up(S, angle), radius)

    R = S
    angle2 = -switches[63].GetOrientationDegrees()
    S = switches[63].GetPosition() + rotate(VECTOR2I(0, half - mil(0.5)), angle2)
    draw_arc_fill_lines(down(R, angle), right(S, angle2), radius)

    R, angle = (S, angle2)
    wradius = radius_wrist_rest
    S = switches[65].GetPosition() + VECTOR2I(-wrist['xoffset'] - 2 * (wradius + dls),
                                              int(wrist['yoffset'] / 2) + half)
    draw_arc_fill_lines(left(R, angle), up(S), wradius)

    center = S + VECTOR2I(-int(wrist['width'] / 2) + 2 * (wradius + dls), mil(0.5))

    R = VECTOR2I(S)
    S += VECTOR2I(wradius + dls, int(wrist['yoffset'] / 2))
    draw_arc_fill_lines(down(R), left(S), wradius)

    S += VECTOR2I(-wrist['width'] + 2 * (wradius + dls), 0)
    draw_wrist(S)

    R = VECTOR2I(S)
    S += VECTOR2I(wradius + dls, -wradius - dls)
    draw_arc_fill_lines(right(R), down(S), wradius)
    R = VECTOR2I(S)
    S += VECTOR2I(-wradius - dls, -wrist['yoffset'] + wradius + offset)
    draw_arc_fill_lines(up(R), right(S), wradius)

    # Right side, starting from bottom middle switch
    R = switches[65].GetPosition() + VECTOR2I(0, half + offset)
    angle = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-half - offset, 0), angle)
    draw_arc_fill_lines(right(R), up(S, angle), radius)

    R = S
    angle2 = -switches[67].GetOrientationDegrees()
    S = switches[67].GetPosition() + rotate(VECTOR2I(0, half - mil(0.5)), angle2)
    draw_arc_fill_lines(down(R, angle), left(S, angle2), radius)

    R, angle = (S, angle2)
    S = switches[65].GetPosition() + VECTOR2I(wrist['xoffset'] + 2 * (wradius + dls),
                                              int(wrist['yoffset'] / 2) + half)
    draw_arc_fill_lines(right(R, angle), up(S), wradius)

    center = S + VECTOR2I(int(wrist['width'] / 2) - 2 * (wradius + dls), mil(0.5))

    R = VECTOR2I(S)
    S += VECTOR2I(-wradius - dls, int(wrist['yoffset'] / 2))
    draw_arc_fill_lines(down(R), right(S), wradius)
    draw_wrist(S)

    S += VECTOR2I(wrist['width'] - 2 * (wradius + dls), 0)
    R = VECTOR2I(S)
    S += VECTOR2I(-wradius - dls, -wradius - dls)
    draw_arc_fill_lines(left(R), down(S), wradius)
    R = VECTOR2I(S)
    S += VECTOR2I(wradius + dls, -wrist['yoffset'] + wradius + offset)
    draw_arc_fill_lines(up(R), left(S), wradius)

def draw_cutout_pcb():
    # Draw left cutout
    R = switches[50].GetPosition() + VECTOR2I(0, half + offset)
    S = switches[61].GetPosition() + VECTOR2I(half + offset, 0)
    draw_arc_fill_lines(left(R), up(S), radius)

    R = S
    angle = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(-half - offset, 0), angle)
    draw_arc_fill_lines(down(R), down(S, angle), radius)

    R, angle2 = (S, angle)
    angle2 = -switches[63].GetOrientationDegrees()
    S = switches[63].GetPosition() + rotate(VECTOR2I(0, -half + mil(1)), angle2)
    draw_arc_fill_lines(up(R, angle), left(S, angle2), radius)

    R, angle = (S, angle2)
    angle2 = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(mil(6), -int(half * 2) - offset), angle2)
    draw_arc_fill_lines(right(R, angle), down(S, angle2), radius)

    R, angle = (S, angle2)
    S = switches[65].GetPosition() + VECTOR2I(-half - offset, -int(half * 0.5))
    draw_arc_fill_lines(right(R, angle), down(S), radius)

    R = S
    S = switches[50].GetPosition() + VECTOR2I(0, half + offset)
    draw_arc_fill_lines(up(R), right(S), radius)

    # Draw right cutout
    R = switches[52].GetPosition() + VECTOR2I(0, half + offset)
    S = switches[69].GetPosition() + VECTOR2I(-half - offset, 0)
    draw_arc_fill_lines(right(R), up(S), radius)

    R, angle = (S, angle2)
    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(half + offset, 0), angle2)
    draw_arc_fill_lines(down(R), down(S, angle2), radius)

    R, angle = (S, angle2)
    angle2 = -switches[67].GetOrientationDegrees()
    S = switches[67].GetPosition() + rotate(VECTOR2I(0, -half - offset + mil(1)), angle2)
    draw_arc_fill_lines(up(R, angle), right(S, angle2), radius)

    R, angle = (S, angle2)
    angle2 = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-mil(6), -int(2 * half) - offset), angle2)
    draw_arc_fill_lines(left(R, angle), down(S, angle2), radius)

    R, angle = (S, angle2)
    S = switches[65].GetPosition() + VECTOR2I(half + offset, -int(half * 0.5))
    draw_arc_fill_lines(left(R, angle), down(S), radius)

    R = S
    S = switches[52].GetPosition() + VECTOR2I(0, half + offset)
    draw_arc_fill_lines(up(R), left(S), radius)


def draw_cutout_plate():
    # Draw left cutout
    R = switches[50].GetPosition() + VECTOR2I(0, half + offset)
    Rstart = R
    angle2 = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(0, -half - offset), angle2)
    draw_arc_fill_lines(left(R), left(S, angle2), radius)

    R, angle = (S, angle2)
    angle2 = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(int(half * 1.75), -half - offset), angle2)
    draw_arc_fill_lines(right(R, angle), left(S, angle2), radius)

    R, angle = (S, angle2)
    S = switches[64].GetPosition() + rotate(VECTOR2I(int(half * 2) + offset, 0), angle2)
    draw_arc_fill_lines(right(R, angle), up(S, angle2), radius_half)

    R, angle = (S, angle2)
    S = switches[65].GetPosition() + VECTOR2I(-half - offset, -int(half * 0.5))
    draw_arc_fill_lines(down(R, angle), down(S), radius)

    R = S
    S = Rstart
    draw_arc_fill_lines(up(R), right(S), radius)

    # Hole
    R = switches[47].GetPosition() + VECTOR2I(int(half * 0.75), half + offset)
    Rstart = R
    S = switches[61].GetPosition() + VECTOR2I(half + offset, 0)
    draw_arc_fill_lines(left(R), up(S), radius)

    R = S
    angle2 = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(-half - offset, 0), angle2)
    draw_arc_fill_lines(down(R), down(S, angle2), radius)

    R, angle = (S, angle2)
    S = Rstart
    draw_arc_fill_lines(up(R, angle), right(S), radius)

    # Draw right cutout
    R = switches[52].GetPosition() + VECTOR2I(0, half + offset)
    Rstart = R
    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(0, -half - offset), angle2)
    draw_arc_fill_lines(right(R), right(S, angle2), radius)

    R, angle = (S, angle2)
    angle2 = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-int(half * 1.5), -half - offset), angle2)
    draw_arc_fill_lines(left(R, angle), right(S, angle2), radius)

    R, angle = (S, angle2)
    S = switches[66].GetPosition() + rotate(VECTOR2I(-int(half * 2) - offset, 0), angle2)
    draw_arc_fill_lines(left(R, angle), up(S, angle2), radius_half)

    R, angle = (S, angle2)
    S = switches[65].GetPosition() + VECTOR2I(half + offset, -int(half * 0.5))
    draw_arc_fill_lines(down(R, angle), down(S), radius)

    R, S = S, Rstart
    draw_arc_fill_lines(up(R), left(S), radius)

    # Hole
    R = switches[55].GetPosition() + VECTOR2I(-int(half * 0.75), half + offset)
    Rstart = R
    S = switches[69].GetPosition() + VECTOR2I(-half - offset, 0)
    draw_arc_fill_lines(right(R), up(S), radius)

    R = S
    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(half + offset, 0), angle2)
    draw_arc_fill_lines(down(R), down(S, angle2), radius)

    R, angle = (S, angle2)
    S = Rstart
    draw_arc_fill_lines(up(R, angle), left(S), radius)


def draw_border(ispcb = False):
    """Draw border."""

    # Draw border from half of one switch to the next, including any arc in
    # between. Start from bottom middle switch and proceed left.
    # (R, S) are start and end points.

    R = switches[65].GetPosition() + VECTOR2I(0, half + offset)
    if ispcb:
        angle = -switches[64].GetOrientationDegrees()
        S = switches[64].GetPosition() + rotate(VECTOR2I(half + offset, 0), angle)
        draw_arc_fill_lines(left(R), up(S, angle), radius)

        R = S
        angle2 = -switches[63].GetOrientationDegrees()
        S = switches[63].GetPosition() + rotate(VECTOR2I(0, half - mil(0.5)), angle2)
        draw_arc_fill_lines(down(R, angle), right(S, angle2), radius)
    else:
        angle = -switches[64].GetOrientationDegrees()
        S = switches[64].GetPosition() + rotate(VECTOR2I(0, half + offset), angle)
        draw_arc_fill_lines(left(R), right(S, angle), radius)

        R = S
        S = switches[64].GetPosition() + rotate(VECTOR2I(-int(half * 2) - offset, 0), angle)
        draw_arc_fill_lines(left(R, angle), down(S, angle), radius)

        R = VECTOR2I(S)
        S += rotate(VECTOR2I(radius + dls, -half - offset), angle)
        draw_arc_fill_lines(up(R, angle), left(S, angle), radius)

        R = S
        angle2 = -switches[63].GetOrientationDegrees()
        S = switches[63].GetPosition() + rotate(VECTOR2I(0, half + offset), angle2)
        draw_arc_fill_lines(right(R, angle), right(S, angle2), radius)

    R, angle = (S, angle2)
    S = switches[61].GetPosition() + VECTOR2I(0, half + offset)
    draw_arc_fill_lines(left(R, angle), right(S), radius)

    R = S
    S = switches[59].GetPosition() + VECTOR2I(-int(half * 1.25) - offset, 0)
    draw_arc_fill_lines(left(R), down(S), radius)

    R = S
    S = switches[45].GetPosition() + VECTOR2I(-half, half + offset)
    draw_arc_fill_lines(up(R), right(S), radius)

    R = S
    S = switches[45].GetPosition() + VECTOR2I(-int(half * 1.25) - offset, 0)
    draw_arc_fill_lines(left(R), down(S), radius)

    R = S
    S = switches[45].GetPosition() + VECTOR2I(-half - offset, -half - offset)
    draw_arc_fill_lines(up(R), left(S), radius)

    R = S
    S = switches[30].GetPosition() + VECTOR2I(-int(half * 1.25) - offset, 0)
    draw_arc_fill_lines(right(R), down(S), radius)

    R = S
    S = switches[30].GetPosition() + VECTOR2I(-half - offset, -half - offset)
    draw_arc_fill_lines(up(R), left(S), radius)

    R = S
    S = switches[16].GetPosition() + VECTOR2I(-int(half * 1.5) - offset, 0)
    draw_arc_fill_lines(right(R), down(S), radius)

    R = S
    S = switches[1].GetPosition() + VECTOR2I(-half, half + offset)
    draw_arc_fill_lines(up(R), right(S), radius)

    R = S
    S = switches[1].GetPosition() + VECTOR2I(-int(half * 1.25) - offset, 0)
    draw_arc_fill_lines(left(R), down(S), radius)

    R = S
    S = switches[15].GetPosition() + VECTOR2I(0, -half - offset)
    draw_arc_fill_lines(up(R), left(S), radius_half)

    # Right side, starting from bottom middle switch
    #
    R = switches[65].GetPosition() + VECTOR2I(0, half + offset)
    if ispcb:
        angle = -switches[66].GetOrientationDegrees()
        S = switches[66].GetPosition() + rotate(VECTOR2I(-half - offset, 0), angle)
        draw_arc_fill_lines(right(R), up(S, angle), radius)

        R = S
        angle2 = -switches[67].GetOrientationDegrees()
        S = switches[67].GetPosition() + rotate(VECTOR2I(0, half - mil(0.5)), angle2)
        draw_arc_fill_lines(down(R, angle), left(S, angle2), radius)
    else:
        angle = -switches[66].GetOrientationDegrees()
        S = switches[66].GetPosition() + rotate(VECTOR2I(0, half + offset), angle)
        draw_arc_fill_lines(right(R), left(S, angle), radius)

        R = S
        S = switches[66].GetPosition() + rotate(VECTOR2I(int(half * 2) - offset, 0), angle)
        draw_arc_fill_lines(right(R, angle), down(S, angle), radius)

        R = VECTOR2I(S)
        S += rotate(VECTOR2I(-radius - dls, -half - offset), angle)
        draw_arc_fill_lines(up(R, angle), right(S, angle), radius)

        R = S
        angle2 = -switches[67].GetOrientationDegrees()
        S = switches[67].GetPosition() + rotate(VECTOR2I(0, half + offset), angle2)
        draw_arc_fill_lines(left(R, angle), left(S, angle2), radius)


    R, angle = (S, angle2)
    S = switches[72].GetPosition() + VECTOR2I(0, half + offset)
    draw_arc_fill_lines(right(R, angle), left(S), radius)

    R = S
    S = switches[72].GetPosition() + VECTOR2I(half + offset, 0)
    draw_arc_fill_lines(right(R), down(S), radius_half)

    R = S
    S = switches[58].GetPosition() + VECTOR2I(int(half * 0.75), half + offset)
    draw_arc_fill_lines(up(R), left(S), radius_half)

    R = S
    S = switches[58].GetPosition() + VECTOR2I(half + offset, 0)
    draw_arc_fill_lines(right(R), down(S), radius_half)

    R = S
    S = switches[15].GetPosition() + VECTOR2I(0, -half - offset)
    draw_arc_fill_lines(up(R), right(S), radius_half)


def remove_border():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        if t.GetLayer() == pcbnew.User_2 or t.GetLayer() == pcbnew.Edge_Cuts:
            board.Delete(t)


# PCB = False  # Plate, not pcb
PCB = True

remove_border()
draw_border(PCB)
if PCB:
    draw_cutout_pcb()
    Layer = pcbnew.User_2
    draw_border(True)
else:
    draw_cutout_plate()
pcbnew.Refresh()
