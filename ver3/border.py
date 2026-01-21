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

from enum import Enum
import math
import pcbnew
from pcbnew import VECTOR2I

mil = lambda x: int(x * 1e6)

SIDE_WALL = mil(4)  # Al sidewall of housing. Plastic bottom cover is inset
                    # by this amount, to give floating effect.

# USB cutout interferes with switch 16 hole
# USB_CUTOUT = [mil(8.7), mil(6)]  # GCT USB4125 connector (5.8mm deep + .2)

Layer = pcbnew.Edge_Cuts

dim = 19.00
COUNT = 72
board = pcbnew.GetBoard()

fillet_radius = mil(1)
fillet_radius_half = mil(0.5)
fillet_radius_laptop = mil(12)  # Macbook Air has 12mm radius corners
fillet_radius_right_bottom = mil(4)

WRIST = {'xoffset': mil(64), 'yoffset': mil(28), 'xwidth': mil(88), 'ywidth': mil(65)}

half = mil(dim / 2)

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]

holes = [board.FindFootprintByReference('H' + str(i)) for i in range(9)]
hole_count  = sum(h is not None for h in holes)

# Create very short directed line segment from vector X, in one of 4 directions.
# 'left' is vector (-delta, 0), etc. 'X' is a directed line segment represented
# by (x, y).
epsilon_dls = mil(0.1) # Length of very small directed line segment after the arc
left = lambda X, angle=0: (X, X + rotate(VECTOR2I(-epsilon_dls, 0), angle))
right = lambda X, angle=0: (X, X + rotate(VECTOR2I(epsilon_dls, 0), angle))
up = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, -epsilon_dls), angle))
down = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, epsilon_dls), angle))



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
    """Rotate a vector by angle theta."""
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
    R = draw_line_arc(down(R), down(S, angle))

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
    R = draw_line_arc(down(R), down(S, angle2))

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
    R = switches[50].GetPosition() + VECTOR2I(0, half)
    Rstart = R
    angle2 = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(0, -half), angle2)
    R = draw_line_arc(left(R), left(S, angle2))

    angle = angle2
    angle2 = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(int(half * 1.75), -half), angle2)
    R = draw_line_arc(right(R, angle), left(S, angle2))

    angle = angle2
    S = switches[64].GetPosition() + rotate(VECTOR2I(int(half * 2), 0), angle2)
    R = draw_line_arc(right(R, angle), up(S, angle2), fillet_radius_half)

    angle = angle2
    S = switches[65].GetPosition() + VECTOR2I(-half, -int(half * 0.5))
    R = draw_line_arc(down(R, angle), down(S))

    S = Rstart
    R = draw_line_arc(up(R), right(S))
    draw_line(R, S)

    # Hole
    R = switches[47].GetPosition() + VECTOR2I(int(half * 0.75), half)
    Rstart = R
    S = switches[61].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(left(R), up(S))

    angle2 = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(-half, 0), angle2)
    R = draw_line_arc(down(R), down(S, angle2))

    angle = angle2
    S = Rstart
    R = draw_line_arc(up(R, angle), right(S))
    draw_line(R, S)

    # Draw right cutout
    R = switches[52].GetPosition() + VECTOR2I(0, half)
    Rstart = R
    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(0, -half), angle2)
    R = draw_line_arc(right(R), right(S, angle2))

    angle = angle2
    angle2 = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-int(half * 1.5), -half), angle2)
    R = draw_line_arc(left(R, angle), right(S, angle2))

    angle = angle2
    S = switches[66].GetPosition() + rotate(VECTOR2I(-int(half * 2), 0), angle2)
    R = draw_line_arc(left(R, angle), up(S, angle2), fillet_radius_half)

    angle = angle2
    S = switches[65].GetPosition() + VECTOR2I(half, -int(half * 0.5))
    R = draw_line_arc(down(R, angle), down(S))

    S = Rstart
    R = draw_line_arc(up(R), left(S))
    draw_line(R, S)

    # Hole
    R = switches[55].GetPosition() + VECTOR2I(-int(half * 0.75), half)
    Rstart = R
    S = switches[69].GetPosition() + VECTOR2I(-half, 0)
    R = draw_line_arc(right(R), up(S))

    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(half, 0), angle2)
    R = draw_line_arc(down(R), down(S, angle2))

    angle = angle2
    S = Rstart
    R = draw_line_arc(up(R, angle), left(S))
    draw_line(R, S)


def draw_wrist():
    """Draw wrist rests."""
    radius = fillet_radius_laptop

    def draw_wrist_inner(A):
        R = A
        S = R + VECTOR2I(-radius, WRIST['ywidth'] - radius)
        R = draw_line_arc(down(R), right(S), radius)
        S = R + VECTOR2I(-WRIST['xwidth'] + radius, -radius)
        R = draw_line_arc(left(R), down(S), radius)
        S = R + VECTOR2I(radius, -WRIST['ywidth'] + radius)
        R = draw_line_arc(up(R), left(S), radius)
        R = draw_line_arc(right(R), up(A), radius)

    A = switches[65].GetPosition() + VECTOR2I(-WRIST['xoffset'], half + WRIST['yoffset'] + radius)
    draw_wrist_inner(A)
    A = switches[65].GetPosition() + VECTOR2I(WRIST['xoffset'] + WRIST['xwidth'],  half + WRIST['yoffset'] + radius)
    draw_wrist_inner(A)


def draw_border():
    """Draw border."""

    # (R, S) are start and end points.
    R = switches[65].GetPosition() + VECTOR2I(0, half)

    angle = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(half, 0), angle)
    R = draw_line_arc(left(R), up(S, angle))

    S = switches[64].GetPosition() + rotate(VECTOR2I(0, int(half * 2)), angle)
    R = draw_line_arc(down(R, angle), right(S, angle))

    S = switches[64].GetPosition() + rotate(VECTOR2I(-half, int(half * 2 - mil(2))), angle)
    R = draw_line_arc(left(R, angle), down(S, angle))

    S = switches[64].GetPosition() + rotate(VECTOR2I(0, int(half * 2 - mil(3.5))), angle)
    R = draw_line_arc(up(R, angle), left(S, angle))

    S = switches[64].GetPosition() + rotate(VECTOR2I(half - mil(3.5), half), angle)
    R = draw_line_arc(right(R, angle), down(S, angle))

    angle2 = -switches[63].GetOrientationDegrees()
    S = switches[63].GetPosition() + rotate(VECTOR2I(0, half), angle2)
    R = draw_line_arc(up(R, angle), right(S, angle2))

    angle = angle2
    S = switches[61].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(left(R, angle), right(S))

    S = switches[65].GetPosition() + VECTOR2I(-WRIST['xoffset'] - WRIST['xwidth'] + SIDE_WALL, 0)
    R = draw_line_arc(left(R), down(S), fillet_radius_laptop - SIDE_WALL)

    RLeft = R

    # Right side, starting from bottom middle switch
    #
    R = switches[65].GetPosition() + VECTOR2I(0, half)

    angle = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-half, 0), angle)
    R = draw_line_arc(right(R), up(S, angle))

    S = switches[66].GetPosition() + rotate(VECTOR2I(0, int(half * 2)), angle)
    R = draw_line_arc(down(R, angle), left(S, angle))

    S = switches[66].GetPosition() + rotate(VECTOR2I(half, int(half * 2 - mil(2))), angle)
    R = draw_line_arc(right(R, angle), down(S, angle))

    S = switches[66].GetPosition() + rotate(VECTOR2I(0, int(half * 2 - mil(3.5))), angle)
    R = draw_line_arc(up(R, angle), right(S, angle))

    S = switches[66].GetPosition() + rotate(VECTOR2I(-half + mil(3.5), half), angle)
    R = draw_line_arc(left(R, angle), down(S, angle))

    angle2 = -switches[67].GetOrientationDegrees()
    S = switches[67].GetPosition() + rotate(VECTOR2I(0, half), angle2)
    R = draw_line_arc(up(R, angle), left(S, angle2))

    angle = angle2
    S = switches[72].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(right(R, angle), left(S))

    S = switches[15].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(right(R), down(S), fillet_radius_right_bottom)

    S = switches[15].GetPosition() + VECTOR2I(0, -half)
    R = draw_line_arc(up(R), right(S), fillet_radius_half)

    # Draw cutout for nrf board's antennae
    S = VECTOR2I(mil(168), -half)
    draw_line(R, S)
    R = S
    S = R + VECTOR2I(-mil(10), mil(3.4))
    R = draw_line_arc(down(R), right(S), fillet_radius_half)
    S = VECTOR2I(mil(156), -half)
    R = draw_line_arc(left(R), down(S), fillet_radius_half)
    draw_line(R, S)
    R = S

    R = draw_line_arc(left(R), up(RLeft), fillet_radius_laptop - SIDE_WALL)
    draw_line(R, RLeft)


def remove_border():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        if t.GetLayer() == pcbnew.User_2 or t.GetLayer() == pcbnew.Edge_Cuts:
            board.Delete(t)


remove_border()
draw_border()

Layer = pcbnew.User_2
draw_wrist()

pcbnew.Refresh()
# board.Save(board.GetFileName())
