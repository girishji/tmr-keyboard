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
from pcbnew import VECTOR2I

mil = lambda x: int(x * 1e6)

LAYER = pcbnew.Edge_Cuts

dim = 19.00
COUNT = 72
board = pcbnew.GetBoard()

SIDE_WALL = mil(7.5)  # 7mm sidewall of housing + .5mm gap
fillet_radius = mil(1)
fillet_radius_half = mil(0.5)
fillet_radius_laptop = mil(12)  # Macbook Air has 12mm radius corners
fillet_radius_right_bottom = mil(4)

# WRIST = {'xoffset': mil(64), 'yoffset': mil(28), 'xwidth': mil(88), 'ywidth': mil(65)}
WRIST_x_offset = mil(64)
WRIST_y_offset = mil(28)
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
    radius = mil(12)

    def draw_wrist_inner(A):
        R = A
        S = R + VECTOR2I(-radius, WRIST_y_length - radius)
        R = draw_line_arc(down(R), right(S), radius)
        S = R + VECTOR2I(-WRIST_x_length + radius, -radius)
        R = draw_line_arc(left(R), down(S), radius)
        S = R + VECTOR2I(radius, -WRIST_y_length + radius)
        R = draw_line_arc(up(R), left(S), radius)
        R = draw_line_arc(right(R), up(A), radius)

    A = switches[65].GetPosition() + VECTOR2I(-WRIST_x_offset, half + WRIST_y_offset + radius)
    draw_wrist_inner(A)
    A = switches[65].GetPosition() + VECTOR2I(WRIST_x_offset + WRIST_x_length,  half + WRIST_y_offset + radius)
    draw_wrist_inner(A)


# Draw Bezier curve using start, end, and 2 control points
def draw_bezier(start_pt, controll, control2, end_pt):
    board = pcbnew.GetBoard()
    bezier_shape = pcbnew.PCB_SHAPE(board)
    bezier_shape.SetShape(pcbnew.SHAPE_T_BEZIER)

    bezier_shape.SetStart(start_pt)
    bezier_shape.SetBezierC1(controll)
    bezier_shape.SetBezierC2(control2)
    bezier_shape.SetEnd(end_pt)

    bezier_shape.SetLayer(LAYER)
    bezier_shape.SetWidth(mil(0.1))
    board.Add(bezier_shape)
    return end_pt


def draw_side_wall_bezier(offset = SIDE_WALL):
    """Draw outer wall using Bezier curves."""

    # Battery (PS5) is 40x61x8.5mm

    left = lambda X, length=mil(0.1), angle=0: X + rotate(VECTOR2I(-length, 0), angle)
    right = lambda X, length=mil(0.1), angle=0: X + rotate(VECTOR2I(length, 0), angle)
    up = lambda X, length=mil(0.1), angle=0: X + rotate(VECTOR2I(0, -length), angle)
    down = lambda X, length=mil(0.1), angle=0: X + rotate(VECTOR2I(0, length), angle)

    # LEFT SIDE

    # Wrist rest
    A = switches[65].GetPosition() + VECTOR2I(0, half)
    T1 = A + VECTOR2I(-WRIST_x_offset - WRIST_x_length, WRIST_y_offset)
    T2 = A + VECTOR2I(-WRIST_x_offset, WRIST_y_offset)
    B2 = A + VECTOR2I(-WRIST_x_offset, WRIST_y_offset + WRIST_y_length)
    B1 = A + VECTOR2I(-WRIST_x_offset - WRIST_x_length, WRIST_y_offset + WRIST_y_length)

    M, N = mil(25), mil(17)

    S = Start = B2 + VECTOR2I(0, -M)
    E = B2 + VECTOR2I(-M, 0)
    S = draw_bezier(S, down(S, N), right(E, N), E)

    E = B1 + VECTOR2I(M, 0)
    S = draw_line(S, E)

    E = B1 + VECTOR2I(0, -M)
    S = draw_bezier(S, left(S, N), down(E, N), E)

    E = T1 + VECTOR2I(0, M)
    S = draw_line(S, E)

    C1 = 11
    P = E = VECTOR2I(switches[59].GetPosition().x - int(half*0.9), T1.y)
    S = draw_bezier(S, up(S, N), left(E, mil(C1)), E)

    C2, C3 = 15, 4
    Q = E = VECTOR2I(mil(69), mil(128))  # 45-deg
    angleQ = -45
    S = draw_bezier(S, right(S, N), left(E, mil(C2), -angleQ), E)
    E = T2 + VECTOR2I(0, M)
    draw_bezier(S, right(S, mil(C3), angleQ+90), up(E, mil(C3)), E)

    draw_line(E, Start)

    # Segment connecting wrist rest to main body
    S = P
    C4 = 12
    E = VECTOR2I(S.x, A.y + offset)
    S = draw_bezier(S, right(S, mil(C4)), right(E, mil(C4)), E)

    # Left wall
    E = VECTOR2I(switches[65].GetPosition().x - WRIST_x_offset - WRIST_x_length, switches[45].GetPosition().y + half)
    S = draw_bezier(S, left(S, mil(10)), down(E, mil(20)), E)

    E = E + VECTOR2I(0, -int(2*half))
    S = draw_line(S, E)

    L_end = E = switches[1].GetPosition() + VECTOR2I(-half, -half - offset)
    S = draw_bezier(S, up(S, mil(25)), left(E, mil(20)), E)

    # Segment connecting wrist rest (right edge of left side)
    S = Q
    C5, C6 = 30, 12
    angle = -switches[62].GetOrientationDegrees()
    E = switches[62].GetPosition() + rotate(VECTOR2I(0, half + offset), angle)
    S = draw_bezier(S, left(S, mil(C5), angleQ+90), left(E, mil(C6), angle), E)

    # Draw curves to the middle key
    C7, C8 = 25, 12
    angle2 = -switches[64].GetOrientationDegrees()
    E = switches[64].GetPosition() + rotate(VECTOR2I(-half, int(2*half) + offset), angle2)
    S = draw_bezier(S, right(S, mil(C7), angle), left(E, mil(C8), angle2), E)

    angle = angle2
    E = S + rotate(VECTOR2I(int(2*half), 0), angle)
    S = draw_line(S, E)

    E = S + rotate(VECTOR2I(offset, -offset), angle)
    S = draw_bezier(S, right(S, int(offset/2), angle), down(E, int(offset/2), angle), E)

    E = S + rotate(VECTOR2I(0, -half), angle)
    S = draw_line(S, E)

    angle2 = -switches[66].GetOrientationDegrees()
    E = switches[66].GetPosition() + rotate(VECTOR2I(-half - offset, half), angle2)
    C = mil(12)
    S = draw_bezier(S, up(S, C, angle), up(E, C, angle2), E)

    # RIGHT SIDE

    angle = angle2
    E = S + rotate(VECTOR2I(0, half), angle)
    S = draw_line(S, E)

    E = S + rotate(VECTOR2I(offset, offset), angle)
    S = draw_bezier(S, down(S, int(offset/2), angle), left(E, int(offset/2), angle), E)

    E = S + rotate(VECTOR2I(int(2*half), 0), angle)
    S = draw_line(S, E)

    # Wrist rest
    A = switches[65].GetPosition() + VECTOR2I(0, half)
    T1 = A + VECTOR2I(WRIST_x_offset + WRIST_x_length, WRIST_y_offset)
    T2 = A + VECTOR2I(WRIST_x_offset, WRIST_y_offset)
    B2 = A + VECTOR2I(WRIST_x_offset, WRIST_y_offset + WRIST_y_length)
    B1 = A + VECTOR2I(WRIST_x_offset + WRIST_x_length, WRIST_y_offset + WRIST_y_length)

    S = Start = B2 + VECTOR2I(0, -M)
    E = B2 + VECTOR2I(M, 0)
    S = draw_bezier(S, down(S, N), left(E, N), E)

    E = B1 + VECTOR2I(-M, 0)
    S = draw_line(S, E)

    E = B1 + VECTOR2I(0, -M)
    S = draw_bezier(S, right(S, N), down(E, N), E)

    E = T1 + VECTOR2I(0, M)
    S = draw_line(S, E)

    P = E = VECTOR2I(A.x + (A.x - P.x), P.y)
    S = draw_bezier(S, up(S, N), right(E, mil(C1)), E)

    Q = E = VECTOR2I(A.x + (A.x - Q.x), Q.y)  # 45-deg
    S = draw_bezier(S, left(S, N), right(E, mil(C2), -angleQ-90), E)
    E = T2 + VECTOR2I(0, M)
    draw_bezier(S, left(S, mil(C3), angleQ), up(E, mil(C3)), E)

    draw_line(E, Start)

    # Segment connecting wrist rest to main body
    S = P
    E = VECTOR2I(S.x, A.y + offset)
    S = draw_bezier(S, left(S, mil(C4)), left(E, mil(C4)), E)

    # Right side wall
    E = switches[72].GetPosition() + VECTOR2I(half, half + offset)
    S = draw_line(S, E)

    # E = E + VECTOR2I(0, -offset) + rotate(VECTOR2I(offset, 0), 45)
    # S = draw_bezier(S, right(S, mil(2)), down(E, mil(2), 45), E)

    E = switches[29].GetPosition() + VECTOR2I(int(1.5*half) + offset, half)
    # S = draw_bezier(S, up(S, mil(8), 45), down(E, mil(16)), E)
    S = draw_bezier(S, right(S, mil(8)), down(E, mil(60)), E)

    E = switches[15].GetPosition() + VECTOR2I(half + offset, -half)
    S = draw_line(S, E)

    E = S + VECTOR2I(-offset, -offset)
    S = draw_bezier(S, up(S, int(offset/2)), right(E, int(offset/2)), E)

    draw_line(S, L_end)

    # Second curve connecting right wrist rest
    S = Q
    angle = -switches[68].GetOrientationDegrees()
    E = switches[68].GetPosition() + rotate(VECTOR2I(0, half + offset), angle)
    S = draw_bezier(S, right(S, mil(C5), angleQ), right(E, mil(C6), angle), E)

    angle2 = -switches[66].GetOrientationDegrees()
    E = switches[66].GetPosition() + rotate(VECTOR2I(half, int(2*half) + offset), angle2)
    S = draw_bezier(S, left(S, mil(C7), angle), right(E, mil(C8), angle2), E)


def draw_side_wall(offset = SIDE_WALL):
    """Draw outer wall."""

    # Left side

    R = switches[65].GetPosition() + VECTOR2I(0, half + offset + mil(2))
    angle = -switches[64].GetOrientationDegrees()
    S = switches[64].GetPosition() + rotate(VECTOR2I(half + offset, int(1.25 * half)), angle)
    R = draw_line_arc(left(R), up(S, angle), offset)

    S = switches[64].GetPosition() + rotate(VECTOR2I(-half, int(half * 2 + offset)), angle)
    R = draw_line_arc(down(R, angle), right(S, angle), offset)

    S = switches[64].GetPosition() + rotate(VECTOR2I(-half - offset, 0), angle)
    R = draw_line_arc(left(R, angle), down(S, angle), offset)

    angle2 = -switches[62].GetOrientationDegrees()
    S = switches[62].GetPosition() + rotate(VECTOR2I(0, int(half + offset)), angle2)
    R = draw_line_arc(up(R, angle), right(S, angle2))

    S = switches[61].GetPosition() + VECTOR2I(0, half + offset)
    R = draw_line_arc(left(R, angle), right(S), offset)

    S = switches[65].GetPosition() + VECTOR2I(-WRIST_x_offset - WRIST_x_length, 0)
    R = draw_line_arc(left(R), down(S), offset)

    RLeft = R

    # Right side

    R = switches[65].GetPosition() + VECTOR2I(0, half + offset + mil(2))
    angle = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(-half - offset, int(1.25 * half)), angle)
    R = draw_line_arc(right(R), up(S, angle), offset)

    S = switches[66].GetPosition() + rotate(VECTOR2I(half, int(half * 2 + offset)), angle)
    R = draw_line_arc(down(R, angle), left(S, angle), offset)

    S = switches[66].GetPosition() + rotate(VECTOR2I(half + offset, 0), angle)
    R = draw_line_arc(right(R, angle), down(S, angle), offset)

    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(0, int(half + offset)), angle2)
    R = draw_line_arc(up(R, angle), left(S, angle2))

    S = switches[72].GetPosition() + VECTOR2I(0, half + offset)
    R = draw_line_arc(right(R, angle), left(S), offset)

    S = switches[15].GetPosition() + VECTOR2I(half + offset, 0)
    R = draw_line_arc(right(R), down(S), fillet_radius_right_bottom + offset)

    S = switches[15].GetPosition() + VECTOR2I(0, -half - offset)
    R = draw_line_arc(up(R), right(S), offset)

    R = draw_line_arc(left(R), up(RLeft), fillet_radius_laptop)

    draw_line(R, RLeft)


def draw_border(ispcb = False):
    """Draw border."""
    global LAYER

    # (R, S) are start and end points.

    R = switches[65].GetPosition() + VECTOR2I(0, half)
    if ispcb:
        angle = -switches[64].GetOrientationDegrees()
        S = switches[64].GetPosition() + rotate(VECTOR2I(half, 0), angle)
        R = draw_line_arc(left(R), up(S, angle))

        angle2 = -switches[63].GetOrientationDegrees()
        S = switches[63].GetPosition() + rotate(VECTOR2I(0, half - mil(0.5)), angle2)
        R = draw_line_arc(down(R, angle), right(S, angle2))
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

    # S = switches[45].GetPosition() + VECTOR2I(-half, half)
    # R = draw_line_arc(up(R), right(S))

    # S = switches[45].GetPosition() + VECTOR2I(-int(half * 1.25), 0)
    # R = draw_line_arc(left(R), down(S))

    # S = switches[45].GetPosition() + VECTOR2I(-half, -half)
    # R = draw_line_arc(up(R), left(S))

    # S = switches[30].GetPosition() + VECTOR2I(-int(half * 1.25), 0)
    # R = draw_line_arc(right(R), down(S))

    S = switches[30].GetPosition() + VECTOR2I(-half, -half)
    R = draw_line_arc(up(R), left(S))

    S = switches[16].GetPosition() + VECTOR2I(-int(half * 1.5), 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[1].GetPosition() + VECTOR2I(0, -half)
    R = draw_line_arc(up(R), left(S))

    S = R + VECTOR2I(mil(3), -mil(5.5))
    R = draw_line_arc(right(R), down(S))

    # Draw USB pcb extension
    if ispcb:
        # S = switches[1].GetPosition() + VECTOR2I(-half, -half - mil(5.5))

        S = S + VECTOR2I(mil(5), 0)
        R = draw_line_arc(up(R), left(S))

        S = R + VECTOR2I(mil(38.5), mil(5))
        R = draw_line_arc(right(R), up(S))

        S = switches[4].GetPosition() + VECTOR2I(0, -half)
        R = draw_line_arc(down(R), left(S))

    RLeft = R

    # Right side, starting from bottom middle switch

    R = switches[65].GetPosition() + VECTOR2I(0, half)
    if ispcb:
        angle = -switches[66].GetOrientationDegrees()
        S = switches[66].GetPosition() + rotate(VECTOR2I(-half, 0), angle)
        R = draw_line_arc(right(R), up(S, angle))

        angle2 = -switches[67].GetOrientationDegrees()
        S = switches[67].GetPosition() + rotate(VECTOR2I(0, half - mil(0.5)), angle2)
        R = draw_line_arc(down(R, angle), left(S, angle2))
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
    S = switches[72].GetPosition() + VECTOR2I(0, half)
    R = draw_line_arc(right(R, angle), left(S))

    S = switches[72].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[44].GetPosition() + VECTOR2I(half, half)
    R = draw_line_arc(up(R), left(S))

    S = switches[44].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[29].GetPosition() + VECTOR2I(int(2*half), half)
    R = draw_line_arc(up(R), left(S))

    S = switches[15].GetPosition() + VECTOR2I(half, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[15].GetPosition() + VECTOR2I(0, -half)
    R = draw_line_arc(up(R), right(S))

    if ispcb:
        # Draw cutout for nrf board's antennae
        S = VECTOR2I(mil(168), -half)
        draw_line(R, S)
        R = S
        S = R + VECTOR2I(-mil(10), mil(3.4))
        R = draw_line_arc(down(R), right(S), fillet_radius_half)
        S = VECTOR2I(mil(155.5), -half)
        R = draw_line_arc(left(R), down(S), fillet_radius_half)
        draw_line(R, S)
        R = S

    if not ispcb:
        R = draw_line_arc(left(R), up(RLeft))
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


def main():
    global LAYER

    if projname() not in ["pcb", "plate"]:
        print(f"Error: unrecognized project {projname()}")
    ispcb = projname() == "pcb"
    print(f"Drawing border... Mode: {'PCB' if ispcb else 'PLATE'}")

    remove_border()
    draw_border(ispcb)

    if ispcb:
        draw_cutout_pcb()
        LAYER = pcbnew.User_5
        draw_wrist()
        draw_side_wall()
        LAYER = pcbnew.User_6
        draw_side_wall_bezier()

    else:
        draw_cutout_plate()

    pcbnew.Refresh()
    # board.Save(board.GetFileName())


main()
