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

# NOTE: There is a 1mm gap between keycaps. Case can be 0.5mm away from
# keycaps, and pcb can be cut exactly where the key footprint ends (leaving
# 0.5mm gap away from the keycap).
# Angle is +ve clockwise, y-axis is +ve downwards

import math
import os
import pcbnew
import csv
from pcbnew import VECTOR2I

mil = lambda x: int(x * 1e6)

LAYER = pcbnew.Edge_Cuts

dim = 19.00
COUNT = 72
board = pcbnew.GetBoard()

GAP = mil(0.5)  # .5mm space between keycap and sidewall
SIDE_WALL = mil(3) + GAP
fillet_radius = mil(1)
# fillet_radius = mil(1.5)  # outer corners for Bakelite
fillet_radius_half = mil(0.5)
# fillet_radius_laptop = mil(12)  # Macbook Air has 12mm radius corners
fillet_radius_laptop = mil(10)  # Fillet of Optical MX keyboard
fillet_radius_right_bottom = mil(4)

CURVES_FILE = "bezier_curves.csv"
Bezier_Curves = []

# WRIST = {'xoffset': mil(64), 'yoffset': mil(28), 'xwidth': mil(88), 'ywidth': mil(65)}
WRIST_x_offset = mil(64)
# WRIST_y_offset = mil(28)
WRIST_y_offset = mil(28+2)  # XXX: Used to be 28
WRIST_x_length = mil(88)
WRIST_y_length = mil(65)

half = mil(dim / 2)

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]

holes = [board.FindFootprintByReference('H' + str(i)) for i in range(9)]
hole_count  = sum(h is not None for h in holes)

# Create directed line segment from vector X, in one of 4 directions.
# 'left' is vector (-delta, 0), etc. 'X' is a directed line segment represented
# by (x, y).
left = lambda X, angle=0: (X, X + rotate(VECTOR2I(-mil(0.1), 0), angle))
right = lambda X, angle=0: (X, X + rotate(VECTOR2I(mil(0.1), 0), angle))
up = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, -mil(0.1)), angle))
down = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, mil(0.1)), angle))

def draw_line(start, end):
    board = pcbnew.GetBoard()
    ls = pcbnew.PCB_SHAPE(board)
    ls.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ls.SetStart(start)
    ls.SetEnd(end)
    ls.SetLayer(LAYER)
    # ls.SetWidth(int(0.12 * pcbnew.IU_PER_MM))
    board.Add(ls)
    return end


def draw_arc(start, mid, end):
    board = pcbnew.GetBoard()
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetArcGeometry(start, mid, end)
    arc.SetLayer(LAYER)
    board.Add(arc)


# Resources:
# Using unit vectors, expressing vector A in terms of B and C, intersection point,
# dot product, cross product, etc.
# A vector is an object that has a magnitude and a direction.
# A Vector is expressed as (x, y) in terms of unit vectors along x, y.
# Directed line segments are written as ((x1, y1), (x2, y2)).
# Below, (A, B, C, ...) are vectors (from origin), and (AB, CD, ...) are
# directed line segments

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


def rotate(V, theta):
    """Rotate a vector by angle theta degrees."""
    sin, cos = (math.sin(math.radians(theta)), math.cos(math.radians(theta)))
    return VECTOR2I(int(cos * V.x - sin * V.y), int(sin * V.x + cos * V.y))


def draw_line_arc(AB, CD, radius=fillet_radius):
    """Draw a line from AB followed by an arc in the dir CD, and return the end pt."""
    A, B, C, D = *AB, *CD
    Eab, Marc, Ecd = arc(A, B, C, D, radius)
    draw_line(A, Eab)
    draw_arc(Eab, Marc, Ecd)
    return Ecd


def place_hole(A, B, C, D):
    """Place mounting hole."""
    I = intersect(A, B, C, D)
    if holes[place_hole.idx]:
        AB, CD = (B - A, D - C)
        offset = fillet - mil(4.0)
        holes[place_hole.idx].SetPosition(I - AB.Resize(offset) - CD.Resize(offset))
        place_hole.idx += 1
place_hole.idx = 1


def draw_cutout_pcb():
    # Draw left cutout
    R = switches[50].GetPosition() + VECTOR2I(0, half)
    Rstart = R
    S = switches[61].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(left(R), up(S))

    angle = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(-half, 0), angle)
    R = draw_line_arc(down(R), down(S, angle), mil(1.5))

    angle2 = -switches[63].GetOrientationDegrees()
    S = switches[63].GetPosition() + rotate(VECTOR2I(0, -half + mil(1)), angle2)
    R = draw_line_arc(up(R, angle), left(S, angle2))

    angle = angle2
    angle2 = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(mil(6), -int(half * 2)), angle2)
    R = draw_line_arc(right(R, angle), down(S, angle2))
    draw_line(R, S)
    R = S

    S = switches[65].GetPosition() + VECTOR2I(-half, -int(half * 0.5))
    R = draw_line_arc(right(R, angle2), down(S))

    S = switches[50].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(up(R), right(S))
    draw_line(R, Rstart)

    # Draw right cutout
    R = switches[52].GetPosition() + VECTOR2I(0, half)
    Rstart = R
    S = switches[69].GetPosition() + VECTOR2I(-half, 0)
    R = draw_line_arc(right(R), up(S))

    angle = angle2
    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(half, 0), angle2)
    R = draw_line_arc(down(R), down(S, angle2), mil(1.5))

    angle = angle2
    angle2 = -switches[67].GetOrientationDegrees()
    S = switches[67].GetPosition() + rotate(VECTOR2I(0, -half + mil(1)), angle2)
    R = draw_line_arc(up(R, angle), right(S, angle2))

    angle = angle2
    angle2 = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-mil(6), -int(2 * half)), angle2)
    R = draw_line_arc(left(R, angle), down(S, angle2))
    draw_line(R, S)
    R = S

    angle = angle2
    S = switches[65].GetPosition() + VECTOR2I(half, -int(half * 0.5))
    R = draw_line_arc(left(R, angle), down(S))

    S = switches[52].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(up(R), left(S))
    draw_line(R, Rstart)


def draw_cutout_plate():
    # Draw left cutout
    WAIST = mil(2.5)
    R = switches[61].GetPosition() + VECTOR2I(0, half + GAP)
    S = switches[61].GetPosition() + VECTOR2I(half + int(GAP/2), 0)
    R = draw_line_arc(right(R), down(S), mil(2))

    S = switches[50].GetPosition() + VECTOR2I(0, half + int(GAP/2))
    R = draw_line_arc(up(R), left(S))

    S = switches[65].GetPosition() + VECTOR2I(-half - GAP, -int(half * 0.5))
    R = draw_line_arc(right(R), up(S))

    angle = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(int(half * 2) + GAP, 0), angle)
    R = draw_line_arc(down(R), down(S, angle))

    S = switches[64].GetPosition() + rotate(VECTOR2I(int(half * 1.75), -half - GAP), angle)
    R = draw_line_arc(up(R, angle), right(S, angle))

    angle2 = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(0, -half - GAP), angle2)
    R = draw_line_arc(left(R, angle), right(S, angle2))

    S = switches[48].GetPosition() + VECTOR2I(-half, half + int(GAP/2) + WAIST)
    R = draw_line_arc(left(R, angle2), right(S))

    S = switches[62].GetPosition() + rotate(VECTOR2I(-half - int(GAP/2), 0), angle2)
    R = draw_line_arc(left(R), up(S, angle2))

    S = switches[62].GetPosition() + rotate(VECTOR2I(0, half + GAP), angle2)
    R = draw_line_arc(down(R, angle2), left(S, angle2), mil(2))

    # Draw right cutout
    R = switches[69].GetPosition() + VECTOR2I(0, half + GAP)
    S = switches[69].GetPosition() + VECTOR2I(-half - int(GAP/2), 0)
    R = draw_line_arc(left(R), down(S), mil(2))

    S = switches[52].GetPosition() + VECTOR2I(0, half + int(GAP/2))
    R = draw_line_arc(up(R), right(S))

    S = switches[65].GetPosition() + VECTOR2I(half + GAP, -int(half * 0.5))
    R = draw_line_arc(left(R), up(S))

    angle = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-int(half * 2) - GAP, 0), angle)
    R = draw_line_arc(down(R), down(S, angle))

    S = switches[66].GetPosition() + rotate(VECTOR2I(-int(half * 1.75), -half - GAP), angle)
    R = draw_line_arc(up(R, angle), left(S, angle))

    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(0, -half - GAP), angle2)
    R = draw_line_arc(right(R, angle), left(S, angle2))

    S = switches[54].GetPosition() + VECTOR2I(half, half + int(GAP/2) + WAIST)
    R = draw_line_arc(right(R, angle2), left(S))

    S = switches[68].GetPosition() + rotate(VECTOR2I(half + int(GAP/2), 0), angle2)
    R = draw_line_arc(right(R), up(S, angle2))

    S = switches[68].GetPosition() + rotate(VECTOR2I(0, half + GAP), angle2)
    R = draw_line_arc(down(R, angle2), right(S, angle2), mil(2))


def draw_wrist():
    """Draw wrist rests."""
    radius = mil(12)

    def draw_wrist_inner(A, rightside=False):
        R = A
        S = R + VECTOR2I(-radius, WRIST_y_length - radius)
        R = draw_line_arc(down(R), right(S), radius)
        if rightside:
            S = R + VECTOR2I(-WRIST_x_length - RIGHT_SIDE_BONUS + radius, -radius)
        else:
            S = R + VECTOR2I(-WRIST_x_length + radius, -radius)
        R = draw_line_arc(left(R), down(S), radius)
        S = R + VECTOR2I(radius, -WRIST_y_length + radius)
        R = draw_line_arc(up(R), left(S), radius)
        R = draw_line_arc(right(R), up(A), radius)

    RIGHT_SIDE_BONUS = mil(5)
    A = switches[65].GetPosition() + VECTOR2I(-WRIST_x_offset, half + WRIST_y_offset + radius)
    draw_wrist_inner(A)
    A = switches[65].GetPosition() + VECTOR2I(WRIST_x_offset + WRIST_x_length + RIGHT_SIDE_BONUS,  half + WRIST_y_offset + radius)
    draw_wrist_inner(A, True)


def draw_border(ispcb = False):
    """Draw border."""
    global LAYER

    # (R, S) are start and end points.
    R = switches[65].GetPosition() + VECTOR2I(0, half)
    if ispcb:
        angle = -switches[64].GetOrientationDegrees()
        S = switches[64].GetPosition() + rotate(VECTOR2I(half, 0), angle)
        R = draw_line_arc(left(R), up(S, angle))

        S = switches[64].GetPosition() + rotate(VECTOR2I(0, half-mil(0.65)), angle)
        R = draw_line_arc(down(R, angle), right(S, angle))

        S = switches[64].GetPosition() + rotate(VECTOR2I(-half-mil(0.4), half), angle)
        R = draw_line_arc(left(R, angle), up(S, angle), fillet_radius_half)

        angle2 = -switches[63].GetOrientationDegrees()
        S = switches[63].GetPosition() + rotate(VECTOR2I(half-mil(0.4), half-mil(0.5)), angle2)
        R = draw_line(R, S)
    else:
        angle = -switches[64].GetOrientationDegrees()
        S = switches[64].GetPosition() + rotate(VECTOR2I(0, half), angle)
        R = draw_line_arc(left(R), right(S, angle))

        S = switches[64].GetPosition() + rotate(VECTOR2I(-int(half * 2), 0), angle)
        R = draw_line_arc(left(R, angle), down(S, angle))

        S = switches[64].GetPosition() + rotate(VECTOR2I(0, -half), angle)
        R = draw_line_arc(up(R, angle), left(S, angle))

        angle2 = -switches[63].GetOrientationDegrees()
        S = switches[63].GetPosition() + rotate(VECTOR2I(0, half), angle2)
        R = draw_line_arc(right(R, angle), right(S, angle2))

    angle = angle2
    S = switches[61].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(left(R, angle), right(S))


    S = switches[59].GetPosition() + VECTOR2I(-int(half * 1.25), 0)
    R = draw_line_arc(left(R), down(S))

    S = switches[45].GetPosition() + VECTOR2I(-half, -half)
    R = draw_line_arc(up(R), left(S))

    S = switches[30].GetPosition() + VECTOR2I(-int(half * 1.25), 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[30].GetPosition() + VECTOR2I(-half, -half)
    R = draw_line_arc(up(R), left(S))

    S = switches[16].GetPosition() + VECTOR2I(-int(half * 1.5), 0)
    R = draw_line_arc(right(R), down(S))

    # Draw USB pcb extension
    # if ispcb:
    #     USB_WIDTH = mil(12)
    #     S = switches[1].GetPosition() + VECTOR2I(-half - mil(6.9), -half + mil(3) + USB_WIDTH)
    #     R = draw_line_arc(up(R), right(S))
    #     R = draw_line(R, S)

    #     S = S + VECTOR2I(0, -USB_WIDTH)
    #     R = draw_line(R, S)

    #     S = switches[1].GetPosition() + VECTOR2I(-half, -half)
    #     R = draw_line_arc(right(R), down(S))

    S = switches[1].GetPosition() + VECTOR2I(0, -half)
    R = draw_line_arc(up(R), left(S))

    # Draw USB pcb extension
    if ispcb:
        USB_WIDTH = mil(11)
        S = switches[1].GetPosition() + VECTOR2I(-half + mil(4), -half - mil(4.9))

        R = draw_line_arc(right(R), down(S))
        R = draw_line(R, S)

        S = R + VECTOR2I(USB_WIDTH, 0)
        R = draw_line(R, S)

        S = switches[2].GetPosition() + VECTOR2I(0, -half)
        R = draw_line_arc(down(R), left(S))

    RLeft = R

    # Right side, starting from bottom middle switch

    R = switches[65].GetPosition() + VECTOR2I(0, half)
    if ispcb:
        angle = -switches[66].GetOrientationDegrees()
        S = switches[66].GetPosition() + rotate(VECTOR2I(-half, 0), angle)
        R = draw_line_arc(right(R), up(S, angle))

        S = switches[66].GetPosition() + rotate(VECTOR2I(0, half-mil(0.65)), angle)
        R = draw_line_arc(down(R, angle), left(S, angle))

        S = switches[66].GetPosition() + rotate(VECTOR2I(half+mil(0.4), half), angle)
        R = draw_line_arc(right(R, angle), up(S, angle), fillet_radius_half)

        angle2 = -switches[67].GetOrientationDegrees()
        S = switches[67].GetPosition() + rotate(VECTOR2I(-half+mil(0.4), half - mil(0.5)), angle2)
        R = draw_line(R, S)

    else:
        angle = -switches[66].GetOrientationDegrees()
        S = switches[66].GetPosition() + rotate(VECTOR2I(0, half), angle)
        R = draw_line_arc(right(R), left(S, angle))

        S = switches[66].GetPosition() + rotate(VECTOR2I(int(half * 2), 0), angle)
        R = draw_line_arc(right(R, angle), down(S, angle))

        S = switches[66].GetPosition() + rotate(VECTOR2I(0, -half), angle)
        R = draw_line_arc(up(R, angle), right(S, angle))

        angle2 = -switches[67].GetOrientationDegrees()
        S = switches[67].GetPosition() + rotate(VECTOR2I(0, half), angle2)
        R = draw_line_arc(left(R, angle), left(S, angle2))

    angle = angle2
    S = switches[70].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(right(R, angle), left(S))

    S = S + VECTOR2I(int(1.25*half), -half)
    R = draw_line_arc(right(R), down(S))

    S = switches[71].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(up(R), left(S))

    S = S + VECTOR2I(half, -half)
    R = draw_line_arc(right(R), down(S))

    S = switches[72].GetPosition() + VECTOR2I(half, half)
    R = draw_line_arc(up(R), left(S))

    S = S + VECTOR2I(0, -half)
    R = draw_line_arc(right(R), down(S))

    S = S + VECTOR2I(-half, -half)
    R = draw_line_arc(up(R), right(S))

    S = switches[15].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(left(R), down(S))

    S = switches[15].GetPosition() + VECTOR2I(0, -half)
    R = draw_line_arc(up(R), right(S))

    if ispcb:
        # Draw cutout for nrf board's antennae
        S = VECTOR2I(mil(175), -half)
        draw_line(R, S)
        R = S
        S = R + VECTOR2I(-mil(6.8), mil(3))
        R = draw_line_arc(down(R), right(S), fillet_radius_half)
        R = draw_line(R, S)
        S = R + VECTOR2I(-mil(10.5), mil(1.55))
        R = draw_line_arc(down(R), right(S), fillet_radius_half)
        S = S + VECTOR2I(0, -mil(3+1.6))
        R = draw_line_arc(left(R), down(S), fillet_radius_half)
        R = draw_line(R, S)

    draw_line(R, RLeft)


def remove_border():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        if t.GetLayer() in [pcbnew.User_5, pcbnew.User_6, pcbnew.Edge_Cuts]:
            board.Delete(t)


def projname():
    board = pcbnew.GetBoard()
    full_path = board.GetFileName()
    filename = os.path.basename(full_path)
    return os.path.splitext(filename)[0]

def get_file_path():
    """
    Constructs the absolute path to the CSV file, typically in the project directory.
    """
    board_path = pcbnew.GetBoard().GetFileName()
    if board_path:
        project_dir = os.path.dirname(board_path)
    else:
        # Fallback if board is not saved, or using KIPRJMOD environment variable
        project_dir = os.getenv("KIPRJMOD", ".")

    return os.path.join(project_dir, CURVES_FILE)


def save_bezier_curves():
    file_path = get_file_path()
    try:
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            for s, c1, c2, e in Bezier_Curves:
                writer.writerow([s.x, s.y, c1.x, c2.y, c2.x, c2.y, e.x, e.y])
        print(f"Successfully saved {len(Bezier_Curves)} curves to {file_path}")
    except IOError as e:
        print(f"Error saving file at {file_path}: {e}")

def main():
    global LAYER

    if projname() not in ["pcb", "plate"]:
        print(f"Error: unrecognized project {projname()}")
    ispcb = projname() == "pcb"
    print(f"Drawing border... Mode: {'PCB' if ispcb else 'PLATE'}")

    remove_border()
    draw_border(ispcb)

    if not ispcb:
        LAYER = pcbnew.User_5
        draw_cutout_plate()
        draw_wrist()

    pcbnew.Refresh()


main()
