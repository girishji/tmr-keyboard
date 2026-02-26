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

KEY_SPACING = 19.00  # Standard key spacing in mm
SWITCH_COUNT = 72
board = pcbnew.GetBoard()

GAP = mil(0.5)  # .5mm space between keycap and sidewall
SIDE_WALL = mil(5) + GAP
fillet_radius = mil(1)
fillet_radius_half = mil(0.5)
fillet_radius_macbook = mil(12)  # Macbook Air has 12mm radius corners
fillet_radius_laptop = mil(10)  # Fillet of Optical MX keyboard
fillet_radius_right_bottom = mil(4)

CURVES_FILE = "bezier_curves.csv"
Bezier_Curves = []

# XXX: SYNC THIS IN placefp.py
WRIST_x_offset = mil(64)
WRIST_y_offset = mil(28+2)  # XXX: Used to be 28
WRIST_x_length = mil(88)
WRIST_y_length = mil(65)
WRIST_right_X_extra = mil(5)

half = mil(KEY_SPACING / 2)

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(SWITCH_COUNT + 1)]

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


def wrist_rest_corners():
    A = switches[65].GetPosition() + VECTOR2I(0, int(mil(KEY_SPACING)/2))
    L1 = A + VECTOR2I(-WRIST_x_offset - WRIST_x_length, WRIST_y_offset)
    L2 = A + VECTOR2I(-WRIST_x_offset, WRIST_y_offset)
    L3 = A + VECTOR2I(-WRIST_x_offset, WRIST_y_offset + WRIST_y_length)
    L4 = A + VECTOR2I(-WRIST_x_offset - WRIST_x_length, WRIST_y_offset + WRIST_y_length)
    R1 = A + VECTOR2I(WRIST_x_offset + WRIST_x_length + WRIST_right_X_extra, WRIST_y_offset)
    R2 = A + VECTOR2I(WRIST_x_offset, WRIST_y_offset)
    R3 = A + VECTOR2I(WRIST_x_offset, WRIST_y_offset + WRIST_y_length)
    R4 = A + VECTOR2I(WRIST_x_offset + WRIST_x_length + WRIST_right_X_extra, WRIST_y_offset + WRIST_y_length)
    return [L1, L2, L3, L4, R1, R2, R3, R4]


def draw_wrist_cavity():
    left = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(-length, 0), angle))
    right = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(length, 0), angle))
    up = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(0, -length), angle))
    down = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(0, length), angle))

    L1, L2, L3, L4, R1, R2, R3, R4 = wrist_rest_corners()
    d, s = mil(20), SIDE_WALL-GAP
    d2, d3, d4 = mil(30), mil(20), mil(18)
    A, B = L1 + VECTOR2I(s, d), L4 + VECTOR2I(s, -d)
    C, D = L3 + VECTOR2I(-d, -s), L4 + VECTOR2I(d, -s)
    E, F = L3 + VECTOR2I(-s, -d), L2 + VECTOR2I(-s, d2)
    G, H = L1 + VECTOR2I(d3, s), L2 + VECTOR2I(-d4, s)
    draw_line(A, B)
    draw_line(C, D)
    draw_line(E, F)
    angle = 7
    GH = H - G
    H = G + rotate(GH, angle)
    draw_line(G, H)
    p, p2 = mil(4), mil(3)
    draw_bezier(*down(B, p), *left(D, p))
    draw_bezier(*right(C, p), *down(E, p))
    draw_bezier(*up(A, p), *left(G, p2, angle))
    draw_bezier(*right(H, p2, angle), *up(F, p2))

    A, B = R1 + VECTOR2I(-s, d), R4 + VECTOR2I(-s, -d)
    C, D = R3 + VECTOR2I(d, -s), R4 + VECTOR2I(-d, -s)
    E, F = R3 + VECTOR2I(s, -d), R2 + VECTOR2I(s, d2)
    G, H = R1 + VECTOR2I(-d3, s), R2 + VECTOR2I(d4, s)
    draw_line(A, B)
    draw_line(C, D)
    draw_line(E, F)
    angle = 10
    GH = H - G
    angle = 6
    H = G + rotate(GH, -angle)
    draw_line(G, H)
    draw_bezier(*down(B, p), *right(D, p))
    draw_bezier(*left(C, p), *down(E, p))
    draw_bezier(*up(A, p), *right(G, p2, -angle))
    draw_bezier(*left(H, mil(3), -angle), *up(F, mil(3)))


# Draw Bezier curve using start, end, and 2 control points
def draw_bezier(start_pt, controll, end_pt, control2):
    global Bezier_Curves

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

    Bezier_Curves.append([start_pt, controll, control2, end_pt])
    return end_pt


def draw_border_bezier(proj=""):
    """Draw outer wall using Bezier curves."""
    global LAYER
    # PS5 battery size is 40x61x8.5mm

    # when two materials meet, they are never perfectly flush because the human
    # eye is incredibly good at spotting a 0.1mm misalignment. By making the
    # middle plate slightly smaller (0.2mm all around) we hide misalignment,
    # provide contrast, and provide relief for "edge beads" common during
    # powder coating.
    reveal = 0
    if proj == "swplate":
        reveal = mil(0.2)

    offset = SIDE_WALL

    left = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(-length, 0), angle))
    right = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(length, 0), angle))
    up = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(0, -length), angle))
    down = lambda X, length=mil(0.1), angle=0: (X, X + rotate(VECTOR2I(0, length), angle))

    # LEFT SIDE

    # Wrist rest
    A = switches[65].GetPosition() + VECTOR2I(0, half)
    T1, T2, B2, B1 = wrist_rest_corners()[:4]
    M, N = mil(24), mil(19)

    S = Start = B2 + VECTOR2I(-reveal, -M)
    E = B2 + VECTOR2I(-M, -reveal)
    S = draw_bezier(*down(S, N), *right(E, N))

    E = B1 + VECTOR2I(M, -reveal)
    S = draw_line(S, E)

    E = B1 + VECTOR2I(reveal, -M)
    S = draw_bezier(*left(S, N), *down(E, N))

    E = T1 + VECTOR2I(reveal, M)
    S = draw_line(S, E)

    # left side top corner
    C1 = 12
    P = E = VECTOR2I(switches[59].GetPosition().x - mil(3) + reveal, T1.y + reveal)
    S = draw_bezier(*up(S, N), *left(E, mil(C1)))

    # 20-deg tangential intermediate point
    C2, C3 = 15, 9
    Q = E = VECTOR2I(mil(59.5) - reveal, mil(122.5) + reveal)
    angleQ = 20
    if proj != "wristrest":
        LAYER = pcbnew.User_6
    S = draw_bezier(*right(S, N), *left(E, mil(C2), angleQ))
    if proj != "wristrest":
        LAYER = pcbnew.Edge_Cuts
    E = T2 + VECTOR2I(-reveal, M)
    draw_bezier(*right(S, mil(C3), angleQ), *up(E, mil(C3)))
    draw_line(E, Start)

    # Segment connecting wrist rest to main body
    S = P
    C4, C4a = 7, 19
    E = VECTOR2I(S.x - mil(7), A.y + offset - reveal)
    S = draw_bezier(*right(S, mil(C4)), *right(E, mil(C4a)))

    # Left wall and top
    E = VECTOR2I(switches[65].GetPosition().x - WRIST_x_offset - WRIST_x_length + reveal, switches[45].GetPosition().y + half)
    S = draw_bezier(*left(S, mil(11)), *down(E, mil(20)))

    E = switches[1].GetPosition() + VECTOR2I(-half + int(0.5*offset) + reveal, -half - offset - mil(1.5) + reveal)
    S = draw_bezier(*up(S, mil(28)), *left(E, mil(17)))

    # draw usb cutout
    Ux = 13.5
    if proj == "swplate":
        E = S + VECTOR2I(mil(1.5), 0)
        S = draw_line(S, E)
        E = S + VECTOR2I(mil(10.5), mil(8.1) - reveal)
        S = draw_line_arc(down(S), left(E), fillet_radius_half)
        E = E + VECTOR2I(0, -mil(8.1) + reveal)
        S = draw_line_arc(right(S), down(E), fillet_radius_half)
        S = draw_line(S, E)
        E = S + VECTOR2I(mil(Ux - 1.5 - 10.5), 0)
        S = draw_line(S, E)

    else:
        E = S + VECTOR2I(mil(Ux), 0)
        S = draw_line(S, E)

    Cn = mil(10)
    E = VECTOR2I(switches[2].GetPosition() + VECTOR2I(half, -half-offset+reveal))
    S = draw_bezier(*right(S, Cn), *left(E, Cn))

    E = switches[4].GetPosition() + VECTOR2I(half, -half - offset+reveal)
    S = draw_line(S, E)

    E = VECTOR2I(switches[5].GetPosition() + VECTOR2I(half, -half-offset-mil(3.5) + reveal))
    S = draw_bezier(*right(S, Cn), *left(E, Cn))

    E = switches[6].GetPosition() + VECTOR2I(half, -half - offset + reveal)
    S = draw_bezier(*right(S, Cn), *left(E, Cn))

    E = switches[9].GetPosition() + VECTOR2I(half, -half - offset + reveal)
    S = draw_line(S, E)

    E = VECTOR2I(switches[10].GetPosition() + VECTOR2I(half, -half-offset-mil(3.5) + reveal))
    S = draw_bezier(*right(S, Cn), *left(E, Cn))

    E = switches[11].GetPosition() + VECTOR2I(half, -half - offset + reveal)
    L_end = S = draw_bezier(*right(S, Cn), *left(E, Cn))

    # Segment connecting wrist rest (right edge of left side)
    S = Q
    C5, C6 = 15, 24
    angle = -switches[62].GetOrientationDegrees()
    E = switches[62].GetPosition() + rotate(VECTOR2I(-reveal, half + offset - reveal), angle)
    S = draw_bezier(*left(S, mil(C5), angleQ), *left(E, mil(C6), angle))

    # Draw curves to the middle key
    C7, C8 = 30, 12
    angle2 = -switches[64].GetOrientationDegrees()
    E = switches[64].GetPosition() + rotate(VECTOR2I(-int(2*half) - offset + reveal, -half), angle2)
    S = draw_bezier(*right(S, mil(C7), angle), *up(E, mil(C8), angle2))

    angle = angle2
    E = S + rotate(VECTOR2I(0, int(2*half)), angle)
    S = draw_line(S, E)

    E = S + rotate(VECTOR2I(offset-reveal, offset-reveal), angle)
    S = draw_bezier(*down(S, int(offset/2), angle), *left(E, int(offset/2), angle))

    E = S + rotate(VECTOR2I(half+reveal, 0), angle)
    S = draw_line(S, E)

    angle2 = -switches[66].GetOrientationDegrees()
    E = switches[66].GetPosition() + rotate(VECTOR2I(half - reveal, half + offset - reveal), angle2)
    C = mil(22)
    S = draw_bezier(*right(S, C, angle), *left(E, C, angle2))

    # RIGHT SIDE

    angle = angle2
    E = S + rotate(VECTOR2I(half, 0), angle)
    S = draw_line(S, E)

    E = S + rotate(VECTOR2I(offset, -offset), angle)
    S = draw_bezier(*right(S, int(offset/2), angle), *down(E, int(offset/2), angle))

    E = S + rotate(VECTOR2I(0, -int(2*half) + reveal), angle)
    S = draw_line(S, E)

    # Wrist rest
    A = switches[65].GetPosition() + VECTOR2I(0, half)
    T1, T2, B2, B1 = wrist_rest_corners()[4:]

    S = Start = B2 + VECTOR2I(reveal, -M)
    E = B2 + VECTOR2I(M, -reveal)
    S = draw_bezier(*down(S, N), *left(E, N))

    E = B1 + VECTOR2I(-M, -reveal)
    S = draw_line(S, E)

    E = B1 + VECTOR2I(-reveal, -M)
    S = draw_bezier(*right(S, N), *down(E, N))

    E = T1 + VECTOR2I(-reveal, M)
    S = draw_line(S, E)

    P = E = VECTOR2I(A.x + (A.x - P.x) + WRIST_right_X_extra - reveal, P.y + reveal)
    S = draw_bezier(*up(S, N), *right(E, mil(C1)))

    E = S + VECTOR2I(-WRIST_right_X_extra, 0)
    if proj != "wristrest":
        LAYER = pcbnew.User_6
    S = draw_line(S, E)
    if proj != "wristrest":
        LAYER = pcbnew.Edge_Cuts

    # 20-deg tangential intermediate point
    Q = E = VECTOR2I(A.x + (A.x - Q.x) + reveal, Q.y + reveal)
    if proj != "wristrest":
        LAYER = pcbnew.User_6
    S = draw_bezier(*left(S, N), *right(E, mil(C2), -angleQ))
    if proj != "wristrest":
        LAYER = pcbnew.Edge_Cuts
    E = T2 + VECTOR2I(reveal, M)
    draw_bezier(*left(S, mil(C3), -angleQ), *up(E, mil(C3)))

    draw_line(E, Start)

    # Segment connecting wrist rest to main body
    S = P
    E = switches[71].GetPosition() + VECTOR2I(-half - reveal, half+offset - reveal)
    S = draw_bezier(*left(S, mil(16)), *left(E, mil(34)))

    W = switches[71].GetPosition() + VECTOR2I(half+int(0.5*offset), 0)
    E = VECTOR2I(W.x - reveal, S.y)
    S = draw_line(S, E)

    # Right side wall
    E = switches[72].GetPosition() + VECTOR2I(half+offset - reveal, 0)
    S = draw_bezier(*right(S, mil(5)), *down(E, mil(20)))

    E = switches[15].GetPosition() + VECTOR2I(half + int(0.3*offset) - reveal, -half - offset + reveal)
    S = draw_bezier(*up(S, mil(24)), *right(E, mil(8)))

    draw_line(S, L_end)

    # Second curve connecting right wrist rest
    S = Q
    angle = -switches[68].GetOrientationDegrees()
    E = switches[68].GetPosition() + rotate(VECTOR2I(reveal, half + offset - reveal), angle)
    S = draw_bezier(*right(S, mil(C5), -angleQ), *right(E, mil(C6), angle))

    angle2 = -switches[66].GetOrientationDegrees()
    E = switches[66].GetPosition() + rotate(VECTOR2I(int(2*half) + offset - reveal, -half), angle2)
    S = draw_bezier(*left(S, mil(C7), angle), *up(E, mil(C8), angle2))


def draw_border(ispcb = False, offset=0):
    """Draw border."""
    global LAYER

    if ispcb and offset != 0:
        print("Error: pcb has non-zero offset")
        return

    # (R, S) are start and end points.
    R = switches[65].GetPosition() + VECTOR2I(0, half+offset)
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
        S = switches[64].GetPosition() + rotate(VECTOR2I(0, half+offset), angle)
        R = draw_line_arc(left(R), right(S, angle))

        S = switches[64].GetPosition() + rotate(VECTOR2I(-int(half * 2)-offset, 0), angle)
        R = draw_line_arc(left(R, angle), down(S, angle))

        S = switches[64].GetPosition() + rotate(VECTOR2I(0, -half-offset), angle)
        R = draw_line_arc(up(R, angle), left(S, angle))

        angle2 = -switches[63].GetOrientationDegrees()
        S = switches[63].GetPosition() + rotate(VECTOR2I(0, half+offset), angle2)
        R = draw_line_arc(right(R, angle), right(S, angle2))

    angle = angle2
    S = switches[61].GetPosition() + VECTOR2I(0, half+offset)
    R = draw_line_arc(left(R, angle), right(S))


    S = switches[59].GetPosition() + VECTOR2I(-int(half * 1.25)-offset, 0)
    R = draw_line_arc(left(R), down(S))

    S = switches[45].GetPosition() + VECTOR2I(-half, -half-offset)
    R = draw_line_arc(up(R), left(S))

    S = switches[30].GetPosition() + VECTOR2I(-int(half * 1.25)-offset, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[30].GetPosition() + VECTOR2I(-half, -half-offset)
    R = draw_line_arc(up(R), left(S))

    S = switches[16].GetPosition() + VECTOR2I(-int(half * 1.5)-offset, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[1].GetPosition() + VECTOR2I(0, -half-offset)
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

    R = switches[65].GetPosition() + VECTOR2I(0, half+offset)
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
        S = switches[66].GetPosition() + rotate(VECTOR2I(0, half+offset), angle)
        R = draw_line_arc(right(R), left(S, angle))

        S = switches[66].GetPosition() + rotate(VECTOR2I(int(half * 2)+offset, 0), angle)
        R = draw_line_arc(right(R, angle), down(S, angle))

        S = switches[66].GetPosition() + rotate(VECTOR2I(0, -half-offset), angle)
        R = draw_line_arc(up(R, angle), right(S, angle))

        angle2 = -switches[67].GetOrientationDegrees()
        S = switches[67].GetPosition() + rotate(VECTOR2I(0, half+offset), angle2)
        R = draw_line_arc(left(R, angle), left(S, angle2))

    angle = angle2
    S = switches[70].GetPosition() + VECTOR2I(0, half+offset)
    R = draw_line_arc(right(R, angle), left(S))

    S = S + VECTOR2I(int(1.25*half)+offset, -half)
    R = draw_line_arc(right(R), down(S))

    S = switches[71].GetPosition() + VECTOR2I(0, half+offset)
    R = draw_line_arc(up(R), left(S))

    S = S + VECTOR2I(half+offset, -half)
    R = draw_line_arc(right(R), down(S))

    S = switches[72].GetPosition() + VECTOR2I(half, half+offset)
    R = draw_line_arc(up(R), left(S))

    S = S + VECTOR2I(offset, -half)
    R = draw_line_arc(right(R), down(S))

    S = S + VECTOR2I(-half, -half-int(2*offset))
    R = draw_line_arc(up(R), right(S))

    S = switches[15].GetPosition() + VECTOR2I(half+offset, 0)
    R = draw_line_arc(left(R), down(S))

    S = switches[15].GetPosition() + VECTOR2I(0, -half-offset)
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

    if projname() not in ["pcb", "swplate", "topcase", "botcase", "cover"]:
        print(f"Error: unrecognized project {projname()}")

    remove_border()

    if projname() == "pcb":
        draw_border(True)
    elif projname() == "swplate":
        draw_border_bezier("swplate")
        draw_wrist_cavity()
        LAYER = pcbnew.User_6
        draw_border(ispcb=False, offset=GAP)
        draw_border(ispcb=False, offset=SIDE_WALL)
        draw_wrist()
    elif projname() == "topcase":
        draw_border(ispcb=False, offset=GAP)
        draw_border_bezier()
        # draw_border(False)
        LAYER = pcbnew.User_6
        draw_border(ispcb=False, offset=SIDE_WALL)
        # draw_cutout_plate()
        draw_wrist()

    pcbnew.Refresh()


main()
