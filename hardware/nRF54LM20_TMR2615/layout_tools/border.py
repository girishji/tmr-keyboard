# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to draw borders

from __future__ import annotations

import csv
import math
import os
from pathlib import Path

from kipy import KiCad
from kipy.board_types import (
    BoardArc,
    BoardBezier,
    BoardLayer,
    BoardSegment,
)
from kipy.geometry import Vector2


# =============================================================================
# CONFIGURATION
# =============================================================================
KEY_SPACING_MM = 19.0
SWITCH_COUNT = 72

GAP_MM = 0.5
SIDE_WALL_MM = 5.0 + GAP_MM

FILLET_RADIUS_MM = 1.0
FILLET_RADIUS_HALF_MM = 0.5
FILLET_RADIUS_MACBOOK_MM = 12.0
FILLET_RADIUS_LAPTOP_MM = 10.0
FILLET_RADIUS_RIGHT_BOTTOM_MM = 4.0

CURVES_FILE = "bezier_curves.csv"

# Keep application-facing dimensions in millimeters.
# Conversion to KiCad nanometer coordinates happens only at geometry boundaries.
WRIST_X_OFFSET_MM = 64.0
WRIST_Y_OFFSET_MM = 30.0
WRIST_X_LENGTH_MM = 88.0
WRIST_Y_LENGTH_MM = 65.0
WRIST_RIGHT_X_EXTRA_MM = 5.0


# =============================================================================
# IPC SESSION / GEOMETRY HELPERS
# =============================================================================
kicad = KiCad()
board = kicad.get_board()


def nm(value_mm: float) -> int:
    """Convert millimeters to KiCad's nanometer integer coordinate unit."""
    return int(round(value_mm * 1_000_000))


def vec_nm(x_nm: int, y_nm: int) -> Vector2:
    """Construct a Vector2 from nanometer coordinates."""
    return Vector2.from_xy(int(x_nm), int(y_nm))


def vec_mm(x_mm: float, y_mm: float) -> Vector2:
    """Construct a Vector2 directly from millimeter coordinates."""
    return Vector2.from_xy_mm(x_mm, y_mm)


def midpoint(a: Vector2, b: Vector2) -> Vector2:
    return vec_nm((a.x + b.x) // 2, (a.y + b.y) // 2)


def dot(a: Vector2, b: Vector2) -> int:
    return a.x * b.x + a.y * b.y


def cross(a: Vector2, b: Vector2) -> int:
    return a.x * b.y - a.y * b.x


def resized(v: Vector2, length_nm: float) -> Vector2:
    """Return v scaled to length_nm, preserving its direction."""
    current = v.length()
    if current == 0:
        raise ValueError("Cannot resize a zero-length vector")
    scale = float(length_nm) / current
    return vec_nm(round(v.x * scale), round(v.y * scale))


def rotate(v: Vector2, angle_deg: float) -> Vector2:
    """Rotate a displacement vector in KiCad screen coordinates."""
    angle = math.radians(angle_deg)
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    return vec_nm(
        round(cos_a * v.x - sin_a * v.y),
        round(sin_a * v.x + cos_a * v.y),
    )


def footprint_map():
    return {
        fp.reference_field.text.value: fp
        for fp in board.get_footprints()
    }


FOOTPRINTS = footprint_map()


def footprint(reference: str):
    fp = FOOTPRINTS.get(reference)
    if fp is None:
        raise RuntimeError(f"Required footprint {reference!r} not found")
    return fp


switches = [None] + [footprint(f"S{i}") for i in range(1, SWITCH_COUNT + 1)]

# Internally the geometry calculations use KiCad integer coordinates because
# intersections, fillets, and shape endpoints operate on Vector2 objects.
GAP = nm(GAP_MM)
SIDE_WALL = nm(SIDE_WALL_MM)
fillet_radius = nm(FILLET_RADIUS_MM)
fillet_radius_half = nm(FILLET_RADIUS_HALF_MM)
fillet_radius_macbook = nm(FILLET_RADIUS_MACBOOK_MM)
fillet_radius_laptop = nm(FILLET_RADIUS_LAPTOP_MM)
fillet_radius_right_bottom = nm(FILLET_RADIUS_RIGHT_BOTTOM_MM)

WRIST_x_offset = nm(WRIST_X_OFFSET_MM)
WRIST_y_offset = nm(WRIST_Y_OFFSET_MM)
WRIST_x_length = nm(WRIST_X_LENGTH_MM)
WRIST_y_length = nm(WRIST_Y_LENGTH_MM)
WRIST_right_X_extra = nm(WRIST_RIGHT_X_EXTRA_MM)

half = nm(KEY_SPACING_MM / 2)

LAYER = BoardLayer.BL_Edge_Cuts
LINE_WIDTH = nm(0.1)

PENDING_SHAPES = []
Bezier_Curves = []

# Create directed line segment from vector X, in one of 4 directions.
# 'left' is vector (-delta, 0), etc. 'X' is a directed line segment represented
# by (x, y).
left = lambda X, angle=0: (X, X + rotate(vec_nm(-nm(0.1), 0), angle))
right = lambda X, angle=0: (X, X + rotate(vec_nm(nm(0.1), 0), angle))
up = lambda X, angle=0: (X, X + rotate(vec_nm(0, -nm(0.1)), angle))
down = lambda X, angle=0: (X, X + rotate(vec_nm(0, nm(0.1)), angle))


def _style_shape(shape):
    shape.layer = LAYER
    shape.attributes.stroke.width = LINE_WIDTH
    PENDING_SHAPES.append(shape)
    return shape


def draw_line(start: Vector2, end: Vector2) -> Vector2:
    segment = BoardSegment()
    segment.start = start
    segment.end = end
    _style_shape(segment)
    return end


def draw_arc(start: Vector2, mid: Vector2, end: Vector2) -> Vector2:
    shape = BoardArc()
    shape.start = start
    shape.mid = mid
    shape.end = end
    _style_shape(shape)
    return end


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
def intersect(P: Vector2, A: Vector2, Q: Vector2, B: Vector2) -> Vector2:
    """Return the intersection of the infinite directed lines PA and QB."""
    r = A - P
    s = B - Q
    rs = cross(r, s)
    if rs == 0:
        raise ValueError("Lines are parallel or degenerate")

    t = cross(Q - P, s) / rs
    return P + resized(r, r.length() * t)


def arc(A, B, C, D, radius):
    """Return tangent start, midpoint, and end points for a fillet arc."""
    intersection = intersect(A, B, C, D)
    ab = B - A
    cd = D - C

    cos_angle = dot(ab, cd) / (ab.length() * cd.length())
    cos_angle = max(-1.0, min(1.0, cos_angle))
    intersection_angle = math.acos(cos_angle)

    tangent_length = radius / math.tan(intersection_angle / 2)
    eab = B + resized(
        ab,
        (intersection - A).length() - ab.length() - tangent_length,
    )
    ecd = D + resized(
        cd,
        (intersection - C).length() - cd.length() - tangent_length,
    )

    mid = midpoint(eab, ecd)
    mid_to_intersection = intersection - mid
    center_to_intersection = math.sqrt(tangent_length**2 + radius**2)
    arc_mid = intersection - resized(
        mid_to_intersection,
        center_to_intersection - radius,
    )
    return eab, arc_mid, ecd


def draw_line_arc(AB, CD, radius=fillet_radius):
    """Draw a line from AB followed by an arc in the dir CD, and return the end pt."""
    A, B, C, D = *AB, *CD
    Eab, Marc, Ecd = arc(A, B, C, D, radius)
    draw_line(A, Eab)
    draw_arc(Eab, Marc, Ecd)
    return Ecd


def draw_cutout_pcb():
    # Draw left cutout
    R = switches[50].position + vec_nm(0, half)
    Rstart = R
    S = switches[61].position + vec_nm(half, 0)
    R = draw_line_arc(left(R), up(S))

    angle = -switches[62].orientation.degrees
    S = switches[62].position + rotate(vec_nm(-half, 0), angle)
    R = draw_line_arc(down(R), down(S, angle), nm(1.5))

    angle2 = -switches[63].orientation.degrees
    S = switches[63].position + rotate(vec_nm(0, -half + nm(1)), angle2)
    R = draw_line_arc(up(R, angle), left(S, angle2))

    angle = angle2
    angle2 = -switches[64].orientation.degrees
    S = switches[64].position + rotate(vec_nm(nm(6), -int(half * 2)), angle2)
    R = draw_line_arc(right(R, angle), down(S, angle2))
    draw_line(R, S)
    R = S

    S = switches[65].position + vec_nm(-half, -int(half * 0.5))
    R = draw_line_arc(right(R, angle2), down(S))

    S = switches[50].position + vec_nm(0, half)
    R = draw_line_arc(up(R), right(S))
    draw_line(R, Rstart)

    # Draw right cutout
    R = switches[52].position + vec_nm(0, half)
    Rstart = R
    S = switches[69].position + vec_nm(-half, 0)
    R = draw_line_arc(right(R), up(S))

    angle = angle2
    angle2 = -switches[68].orientation.degrees
    S = switches[68].position + rotate(vec_nm(half, 0), angle2)
    R = draw_line_arc(down(R), down(S, angle2), nm(1.5))

    angle = angle2
    angle2 = -switches[67].orientation.degrees
    S = switches[67].position + rotate(vec_nm(0, -half + nm(1)), angle2)
    R = draw_line_arc(up(R, angle), right(S, angle2))

    angle = angle2
    angle2 = -switches[66].orientation.degrees
    S = switches[66].position + rotate(vec_nm(-nm(6), -int(2 * half)), angle2)
    R = draw_line_arc(left(R, angle), down(S, angle2))
    draw_line(R, S)
    R = S

    angle = angle2
    S = switches[65].position + vec_nm(half, -int(half * 0.5))
    R = draw_line_arc(left(R, angle), down(S))

    S = switches[52].position + vec_nm(0, half)
    R = draw_line_arc(up(R), left(S))
    draw_line(R, Rstart)


def draw_cutout_plate():
    # Draw left cutout
    WAIST = nm(2.5)
    R = switches[61].position + vec_nm(0, half + GAP)
    S = switches[61].position + vec_nm(half + int(GAP/2), 0)
    R = draw_line_arc(right(R), down(S), nm(2))

    S = switches[50].position + vec_nm(0, half + int(GAP/2))
    R = draw_line_arc(up(R), left(S))

    S = switches[65].position + vec_nm(-half - GAP, -int(half * 0.5))
    R = draw_line_arc(right(R), up(S))

    angle = -switches[64].orientation.degrees
    S = switches[64].position + rotate(vec_nm(int(half * 2) + GAP, 0), angle)
    R = draw_line_arc(down(R), down(S, angle))

    S = switches[64].position + rotate(vec_nm(int(half * 1.75), -half - GAP), angle)
    R = draw_line_arc(up(R, angle), right(S, angle))

    S = switches[63].position + rotate(vec_nm(int(half * 1.25) + GAP, 0), angle)
    R = draw_line_arc(left(R, angle), down(S, angle))

    S = switches[63].position + rotate(vec_nm(half, -half-GAP), angle)
    R = draw_line_arc(up(R, angle), right(S, angle))

    angle2 = -switches[62].orientation.degrees
    S = switches[62].position + rotate(vec_nm(0, -half - GAP), angle2)
    R = draw_line_arc(left(R, angle), right(S, angle2))

    S = switches[48].position + vec_nm(-half, half + int(GAP/2) + WAIST)
    R = draw_line_arc(left(R, angle2), right(S))

    S = switches[62].position + rotate(vec_nm(-half - int(GAP/2), 0), angle2)
    R = draw_line_arc(left(R), up(S, angle2))

    S = switches[62].position + rotate(vec_nm(0, half + GAP), angle2)
    R = draw_line_arc(down(R, angle2), left(S, angle2), nm(2))
    R = draw_line(R, S)

    # Draw right cutout
    R = switches[69].position + vec_nm(0, half + GAP)
    S = switches[69].position + vec_nm(-half - int(GAP/2), 0)
    R = draw_line_arc(left(R), down(S), nm(2))

    S = switches[52].position + vec_nm(0, half + int(GAP/2))
    R = draw_line_arc(up(R), right(S))

    S = switches[65].position + vec_nm(half + GAP, -int(half * 0.5))
    R = draw_line_arc(left(R), up(S))

    angle = -switches[66].orientation.degrees
    S = switches[66].position + rotate(vec_nm(-int(half * 2) - GAP, 0), angle)
    R = draw_line_arc(down(R), down(S, angle))

    S = switches[66].position + rotate(vec_nm(-int(half * 1.75), -half - GAP), angle)
    R = draw_line_arc(up(R, angle), left(S, angle))

    angle2 = -switches[68].orientation.degrees
    S = switches[68].position + rotate(vec_nm(0, -half - GAP), angle2)
    R = draw_line_arc(right(R, angle), left(S, angle2))

    S = switches[54].position + vec_nm(half, half + int(GAP/2) + WAIST)
    R = draw_line_arc(right(R, angle2), left(S))

    S = switches[68].position + rotate(vec_nm(half + int(GAP/2), 0), angle2)
    R = draw_line_arc(right(R), up(S, angle2))

    S = switches[68].position + rotate(vec_nm(0, half + GAP), angle2)
    R = draw_line_arc(down(R, angle2), right(S, angle2), nm(2))
    draw_line(R, S)


def draw_wrist():
    """Draw wrist rests."""
    radius = nm(12)

    def draw_wrist_inner(A, rightside=False):
        R = A
        S = R + vec_nm(-radius, WRIST_y_length - radius)
        R = draw_line_arc(down(R), right(S), radius)
        if rightside:
            S = R + vec_nm(-WRIST_x_length - RIGHT_SIDE_BONUS + radius, -radius)
        else:
            S = R + vec_nm(-WRIST_x_length + radius, -radius)
        R = draw_line_arc(left(R), down(S), radius)
        S = R + vec_nm(radius, -WRIST_y_length + radius)
        R = draw_line_arc(up(R), left(S), radius)
        R = draw_line_arc(right(R), up(A), radius)

    RIGHT_SIDE_BONUS = nm(5)
    A = switches[65].position + vec_nm(-WRIST_x_offset, half + WRIST_y_offset + radius)
    draw_wrist_inner(A)
    A = switches[65].position + vec_nm(WRIST_x_offset + WRIST_x_length + RIGHT_SIDE_BONUS,  half + WRIST_y_offset + radius)
    draw_wrist_inner(A, True)


def wrist_rest_corners():
    A = switches[65].position + vec_nm(0, int(nm(KEY_SPACING_MM)/2))
    L1 = A + vec_nm(-WRIST_x_offset - WRIST_x_length, WRIST_y_offset)
    L2 = A + vec_nm(-WRIST_x_offset, WRIST_y_offset)
    L3 = A + vec_nm(-WRIST_x_offset, WRIST_y_offset + WRIST_y_length)
    L4 = A + vec_nm(-WRIST_x_offset - WRIST_x_length, WRIST_y_offset + WRIST_y_length)
    R1 = A + vec_nm(WRIST_x_offset + WRIST_x_length + WRIST_right_X_extra, WRIST_y_offset)
    R2 = A + vec_nm(WRIST_x_offset, WRIST_y_offset)
    R3 = A + vec_nm(WRIST_x_offset, WRIST_y_offset + WRIST_y_length)
    R4 = A + vec_nm(WRIST_x_offset + WRIST_x_length + WRIST_right_X_extra, WRIST_y_offset + WRIST_y_length)
    return [L1, L2, L3, L4, R1, R2, R3, R4]


def draw_wrist_cavity():
    left = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(-length, 0), angle))
    right = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(length, 0), angle))
    up = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(0, -length), angle))
    down = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(0, length), angle))

    L1, L2, L3, L4, R1, R2, R3, R4 = wrist_rest_corners()
    d, s = nm(20), SIDE_WALL-GAP
    d2, d3, d4 = nm(30), nm(20), nm(18)
    A, B = L1 + vec_nm(s, d), L4 + vec_nm(s, -d)
    C, D = L3 + vec_nm(-d, -s), L4 + vec_nm(d, -s)
    E, F = L3 + vec_nm(-s, -d), L2 + vec_nm(-s, d2)
    G, H = L1 + vec_nm(d3, s), L2 + vec_nm(-d4, s)
    draw_line(A, B)
    draw_line(C, D)
    draw_line(E, F)
    angle = 7
    GH = H - G
    H = G + rotate(GH, angle)
    draw_line(G, H)
    p, p2 = nm(4), nm(3)
    draw_bezier(*down(B, p), *left(D, p))
    draw_bezier(*right(C, p), *down(E, p))
    draw_bezier(*up(A, p), *left(G, p2, angle))
    draw_bezier(*right(H, p2, angle), *up(F, p2))

    A, B = R1 + vec_nm(-s, d), R4 + vec_nm(-s, -d)
    C, D = R3 + vec_nm(d, -s), R4 + vec_nm(-d, -s)
    E, F = R3 + vec_nm(s, -d), R2 + vec_nm(s, d2)
    G, H = R1 + vec_nm(-d3, s), R2 + vec_nm(d4, s)
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
    draw_bezier(*left(H, nm(3), -angle), *up(F, nm(3)))


# Draw a cubic Bezier using start, two control points, and end.
def draw_bezier(start_pt, control1, end_pt, control2):
    shape = BoardBezier()
    shape.start = start_pt
    shape.control1 = control1
    shape.control2 = control2
    shape.end = end_pt
    _style_shape(shape)

    Bezier_Curves.append((start_pt, control1, control2, end_pt))
    return end_pt


def draw_wristrest_border_bezier(proj="", reveal=0):
    global LAYER

    left = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(-length, 0), angle))
    right = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(length, 0), angle))
    up = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(0, -length), angle))
    down = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(0, length), angle))

    # Left wrist rest
    A = switches[65].position + vec_nm(0, half)
    T1, T2, B2, B1 = wrist_rest_corners()[:4]
    M, N = nm(24), nm(19)

    S = Start = B2 + vec_nm(-reveal, -M)
    E = B2 + vec_nm(-M, -reveal)
    S = draw_bezier(*down(S, N), *right(E, N))

    E = B1 + vec_nm(M, -reveal)
    S = draw_line(S, E)

    E = B1 + vec_nm(reveal, -M)
    S = draw_bezier(*left(S, N), *down(E, N))

    E = T1 + vec_nm(reveal, M)
    S = draw_line(S, E)

    # left side top corner of wrist rest
    C1 = 12
    P1 = E = vec_nm(switches[59].position.x - nm(3) + reveal, T1.y + reveal)
    S = draw_bezier(*up(S, N), *left(E, nm(C1)))

    # angled tangential pt
    C2, C3 = 15, 6.5
    Q1 = E = vec_nm(nm(65.5) - reveal, nm(125) + reveal)
    angleQ = 38
    edge_cuts = (LAYER == BoardLayer.BL_Edge_Cuts)
    if edge_cuts:
        LAYER = BoardLayer.BL_User_8
    S = draw_bezier(*right(S, N), *left(E, nm(C2), angleQ))
    if edge_cuts:
        LAYER = BoardLayer.BL_Edge_Cuts
    E = T2 + vec_nm(-reveal, M)
    draw_bezier(*right(S, nm(C3), angleQ), *up(E, nm(C3)))
    draw_line(E, Start)

    # Right wrist rest
    A = switches[65].position + vec_nm(0, half)
    T1, T2, B2, B1 = wrist_rest_corners()[4:]

    S = Start = B2 + vec_nm(reveal, -M)
    E = B2 + vec_nm(M, -reveal)
    S = draw_bezier(*down(S, N), *left(E, N))

    E = B1 + vec_nm(-M, -reveal)
    S = draw_line(S, E)

    E = B1 + vec_nm(-reveal, -M)
    S = draw_bezier(*right(S, N), *down(E, N))

    E = T1 + vec_nm(-reveal, M)
    S = draw_line(S, E)

    P2 = E = vec_nm(A.x + (A.x - P1.x) + WRIST_right_X_extra - reveal, P1.y)
    S = draw_bezier(*up(S, N), *right(E, nm(C1)))

    E = S + vec_nm(-WRIST_right_X_extra, 0)
    if edge_cuts:
        LAYER = BoardLayer.BL_User_8
    S = draw_line(S, E)
    if edge_cuts:
        LAYER = BoardLayer.BL_Edge_Cuts

    # 20-deg tangential intermediate point
    Q2 = E = vec_nm(A.x + (A.x - Q1.x), Q1.y)
    if edge_cuts:
        LAYER = BoardLayer.BL_User_8
    S = draw_bezier(*left(S, N), *right(E, nm(C2), -angleQ))
    if edge_cuts:
        LAYER = BoardLayer.BL_Edge_Cuts
    E = T2 + vec_nm(reveal, M)
    draw_bezier(*left(S, nm(C3), -angleQ), *up(E, nm(C3)))

    draw_line(E, Start)

    return (P1, Q1, P2, Q2, angleQ)


def draw_border_bezier(proj="", reveal=0, usb_cutout=True, wire_cutout=False):
    """Draw outer wall using Bezier curves."""
    # 'reveal': when two layers meet (one on top of another), they are never perfectly
    # flush because the human eye is good at spotting a 0.1mm misalignment. By
    # making the middle plate slightly smaller (0.2mm all around) we hide misalignment,
    # and provide relief for "edge beads" common during powder coating.

    # PS5 battery size is 40x61x8.5mm

    if proj == "wristrest":
        draw_wristrest_border_bezier(proj, reveal)
        return

    offset = SIDE_WALL

    P1, Q1, P2, Q2, angleQ = draw_wristrest_border_bezier(proj, reveal)

    left = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(-length, 0), angle))
    right = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(length, 0), angle))
    up = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(0, -length), angle))
    down = lambda X, length=nm(0.1), angle=0: (X, X + rotate(vec_nm(0, length), angle))

    # LEFT SIDE

    # Segment connecting left wrist rest to main body
    S = P1
    A = switches[65].position + vec_nm(0, half)
    C4, C4a = 35, 17
    E = vec_nm(S.x - nm(7), A.y + offset - reveal)
    S = draw_bezier(*right(S, nm(C4)), *right(E, nm(C4a)))

    # Left wall and top
    E = vec_nm(switches[65].position.x - WRIST_x_offset - WRIST_x_length + reveal, switches[45].position.y + half)
    S = draw_bezier(*left(S, nm(11)), *down(E, nm(20)))

    E = switches[1].position + vec_nm(-half + int(0.5*offset), -half - offset - nm(3.3) + reveal)
    S = draw_bezier(*up(S, nm(28)), *left(E, nm(17)))

    # draw usb cutout
    width_usb = nm(10.6)
    usb_start = nm(1.9)
    if usb_cutout:
        usb_depth = nm(9)
        E = S + vec_nm(usb_start, 0)
        S = draw_line(S, E)
        E = S + vec_nm(width_usb, usb_depth - reveal)
        S = draw_line_arc(down(S), left(E), fillet_radius_half)
        E = E + vec_nm(0, -usb_depth + reveal)
        S = draw_line_arc(right(S), down(E), fillet_radius_half)
        S = draw_line(S, E)
    else:
        E = S + vec_nm(usb_start + width_usb, 0)
        S = draw_line(S, E)

    Cn, Cm = nm(6), nm(30)

    top_max_thickness = offset + nm(3.6) - reveal
    top_min_thickness = offset + nm(2) - reveal

    H2x = footprint('H2').position.x
    H3x = footprint('H3').position.x
    H4x = footprint('H4').position.x
    Sw5topY = switches[5].position.y - half

    E = vec_nm(int((S.x + H2x) / 2), Sw5topY-top_min_thickness)
    S = S_save = draw_bezier(*right(S, Cn), *left(E, Cm))

    E = vec_nm(H2x, Sw5topY-top_max_thickness)
    S = S_save = draw_bezier(*right(S, Cm), *left(E, Cn))

    # cutout for ble antenna
    if proj == "botcover":
        S = switches[8].position + vec_nm(nm(5), -half + nm(4.5))
        E = S + vec_nm(0, -nm(5))
        S = draw_line(S, E)
        E = S + vec_nm(nm(11), 0)
        S = draw_line(S, E)
        E = S + vec_nm(0, nm(5))
        S = draw_line(S, E)
        E = S + vec_nm(-nm(11), 0)
        S = draw_line(S, E)
        S = S_save
    elif proj == "swplate":
        # BLE module b/w sw8 & sw9
        S = switches[8].position + vec_nm(nm(-5), -half-top_min_thickness+reveal+nm(2))
        E = S + vec_nm(0, nm(5))
        S = draw_line(S, E)
        E = S + vec_nm(half+half+nm(10), 0)
        S = draw_line(S, E)
        E = S + vec_nm(0, -nm(5))
        S = draw_line(S, E)
        E = S + vec_nm(-half-half-nm(10), 0)
        S = draw_line(S, E)
        S = S_save

    E = vec_nm(int((H3x + H2x) / 2), Sw5topY-top_min_thickness)
    S = draw_bezier(*right(S, Cn), *left(E, Cm))

    E = vec_nm(H3x, Sw5topY-top_max_thickness)
    S = draw_bezier(*right(S, Cm), *left(E, Cn))

    E = vec_nm(int((H4x + H3x) / 2), Sw5topY-top_min_thickness)
    S = draw_bezier(*right(S, Cn), *left(E, Cm))

    E = vec_nm(H4x, Sw5topY-top_max_thickness)
    L_end = S = draw_bezier(*right(S, Cm), *left(E, Cn))

    # Segment connecting wrist rest (right edge of left side)
    S = Q1
    C5, C6 = 52, 24
    angle = -switches[62].orientation.degrees
    E = switches[62].position + rotate(vec_nm(-reveal, half + offset - reveal), angle)
    S = draw_bezier(*left(S, nm(C5), angleQ), *left(E, nm(C6), angle))

    # Draw curves to the middle key
    C7, C8 = 30, 12
    angle2 = -switches[64].orientation.degrees
    E = switches[64].position + rotate(vec_nm(-int(2*half) - offset + reveal, -half), angle2)
    S = draw_bezier(*right(S, nm(C7), angle), *up(E, nm(C8), angle2))

    angle = angle2
    E = S + rotate(vec_nm(0, int(2*half)), angle)
    S = draw_line(S, E)

    E = S + rotate(vec_nm(offset-reveal, offset-reveal), angle)
    S = draw_bezier(*down(S, int(offset/2), angle), *left(E, int(offset/2), angle))

    E = S + rotate(vec_nm(half+reveal, 0), angle)
    S = draw_line(S, E)

    angle2 = -switches[66].orientation.degrees
    E = switches[66].position + rotate(vec_nm(half - reveal, half + offset - reveal), angle2)
    C = nm(22)
    S = draw_bezier(*right(S, C, angle), *left(E, C, angle2))

    # RIGHT SIDE

    angle = angle2
    E = S + rotate(vec_nm(half, 0), angle)
    S = draw_line(S, E)

    E = S + rotate(vec_nm(offset, -offset), angle)
    S = draw_bezier(*right(S, int(offset/2), angle), *down(E, int(offset/2), angle))

    E = S + rotate(vec_nm(0, -int(2*half) + reveal), angle)
    S = draw_line(S, E)

    # Segment connecting right wrist rest to main body
    S = P2
    Cr1, Cr2 = 38, 29
    E = switches[72].position + vec_nm(0, half+offset - reveal)
    S = draw_bezier(*left(S, nm(Cr1)), *left(E, nm(Cr2)))

    E = S + vec_nm(half-reveal, 0)
    S = draw_line(S, E)

    # Right side wall
    E = switches[72].position + vec_nm(half+offset-reveal, half)
    S = draw_bezier(*right(S, offset-reveal), *down(E, offset-reveal))

    E = switches[15].position + vec_nm(half+offset-reveal, 0)
    S = draw_line(S, E)
    S = draw_bezier(*up(S, nm(10)), *right(L_end, nm(9)))

    # Second curve connecting right wrist rest
    S = Q2
    angle = -switches[68].orientation.degrees
    E = switches[68].position + rotate(vec_nm(reveal, half + offset - reveal), angle)
    S = draw_bezier(*right(S, nm(C5), -angleQ), *right(E, nm(C6), angle))

    angle2 = -switches[66].orientation.degrees
    E = switches[66].position + rotate(vec_nm(int(2*half) + offset - reveal, -half), angle2)
    S = draw_bezier(*left(S, nm(C7), angle), *up(E, nm(C8), angle2))

    # cutout for wires
    if wire_cutout:
        def wire_cutout(S):
            W, L = nm(2), nm(33)
            E = S + vec_nm(W, 0)
            S = draw_line(S, E)
            E = S + vec_nm(0, L)
            S = draw_line(S, E)
            E = S + vec_nm(-W, 0)
            S = draw_line(S, E)
            E = S + vec_nm(0, -L)
            S = draw_line(S, E)
        S = S_save = switches[60].position + vec_nm(0, half+GAP+nm(2))
        wire_cutout(S)
        S = S_save = switches[70].position + vec_nm(-nm(2), half+GAP+nm(2))
        wire_cutout(S)


def draw_border(proj, offset=0, cutout=False):
    """Draw border."""
    global LAYER

    ispcb = proj == "pcb"
    if ispcb and offset != 0:
        print("Error: pcb has non-zero offset")
        return

    # (R, S) are start and end points.
    R = switches[65].position + vec_nm(0, half+offset)
    if ispcb:
        angle = -switches[64].orientation.degrees
        S = switches[64].position + rotate(vec_nm(0, half), angle)
        R = draw_line_arc(left(R), right(S, angle))

        S = switches[64].position + rotate(vec_nm(-half+nm(0.65), 0), angle)
        R = draw_line_arc(left(R, angle), down(S, angle))

        S = switches[64].position + rotate(vec_nm(-half, -half-nm(0.4)), angle)
        R = draw_line_arc(up(R, angle), left(S, angle), fillet_radius_half)

        angle2 = -switches[63].orientation.degrees
        S = switches[63].position + rotate(vec_nm(-int(half * 5/4)+nm(0.5), half-nm(0.4)), angle2)
        R = draw_line(R, S)

        angle2 = -switches[62].orientation.degrees
    else:
        angle = -switches[64].orientation.degrees
        S = switches[64].position + rotate(vec_nm(0, half+offset), angle)
        R = draw_line_arc(left(R), right(S, angle))

        S = switches[64].position + rotate(vec_nm(-int(half * 2)-offset, 0), angle)
        R = draw_line_arc(left(R, angle), down(S, angle))

        S = switches[64].position + rotate(vec_nm(0, -half-offset), angle)
        R = draw_line_arc(up(R, angle), left(S, angle))

        angle2 = -switches[62].orientation.degrees
        S = switches[62].position + rotate(vec_nm(0, half+offset), angle2)
        R = draw_line_arc(right(R, angle), right(S, angle2))

    angle = angle2

    if cutout and offset == GAP:
        S = switches[62].position + rotate(vec_nm(0, half + GAP), angle2)
        draw_line(R, S)
        R = switches[61].position + vec_nm(0, half+offset)
    else:
        S = switches[61].position + vec_nm(0, half+offset)
        R = draw_line_arc(left(R, angle), right(S))

    S = switches[59].position + vec_nm(-int(half * 1.25)-offset, 0)
    R = draw_line_arc(left(R), down(S))

    S = switches[45].position + vec_nm(-half, -half-offset)
    R = draw_line_arc(up(R), left(S))

    S = switches[30].position + vec_nm(-int(half * 1.25)-offset, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[30].position + vec_nm(-half, -half-offset)
    R = draw_line_arc(up(R), left(S))

    S = switches[16].position + vec_nm(-int(half * 1.5)-offset, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[1].position + vec_nm(0, -half-offset)
    R = draw_line_arc(up(R), left(S))

    # Draw usb pcb extension
    USB_WIDTH = nm(11)
    if ispcb:
        S = switches[1].position + vec_nm(-half + nm(3.5), -half - nm(6.6))

        R = draw_line_arc(right(R), down(S))
        R = draw_line(R, S)

        S = R + vec_nm(nm(13), 0)
        R = draw_line(R, S)

        S = switches[3].position + vec_nm(0, -half)
        R = draw_line_arc(down(R), left(S))

    # draw cutout for pcb extension holding usb receptacle
    elif proj == "botcase" and offset == GAP:
        S = switches[1].position + vec_nm(-half + nm(3.5), -half - nm(5.1))

        R = draw_line_arc(right(R), down(S))
        R = draw_line(R, S)

        S = R + vec_nm(USB_WIDTH + nm(1), 0)
        R = draw_line(R, S)

        # cutout for ble antenna
        S = switches[8].position + vec_nm(0, -half - offset)
        R = draw_line_arc(down(R), left(S))
        R = draw_line(R, S)
        S = S + vec_nm(0, -nm(3.5))
        R = draw_line(R, S)
        S = R + vec_nm(nm(29), 0)
        R = draw_line(R, S)
        S = R + vec_nm(0, nm(3.5))
        R = draw_line(R, S)

    RLeft = R

    # Right side, starting from bottom middle switch

    R = switches[65].position + vec_nm(0, half+offset)
    if ispcb:
        angle = -switches[66].orientation.degrees
        S = switches[66].position + rotate(vec_nm(0, half), angle)
        R = draw_line_arc(right(R), left(S, angle))

        S = switches[66].position + rotate(vec_nm(half-nm(0.65), 0), angle)
        R = draw_line_arc(right(R, angle), down(S, angle))

        S = switches[66].position + rotate(vec_nm(half, -half-nm(0.4)), angle)
        R = draw_line_arc(up(R, angle), left(S, angle), fillet_radius_half)

        angle2 = -switches[67].orientation.degrees
        S = switches[67].position + rotate(vec_nm(-half+nm(0.4), half - nm(0.5)), angle2)
        R = draw_line(R, S)

    else:
        angle = -switches[66].orientation.degrees
        S = switches[66].position + rotate(vec_nm(0, half+offset), angle)
        R = draw_line_arc(right(R), left(S, angle))

        S = switches[66].position + rotate(vec_nm(int(half * 2)+offset, 0), angle)
        R = draw_line_arc(right(R, angle), down(S, angle))

        S = switches[66].position + rotate(vec_nm(0, -half-offset), angle)
        R = draw_line_arc(up(R, angle), right(S, angle))

        angle2 = -switches[67].orientation.degrees
        S = switches[67].position + rotate(vec_nm(0, half+offset), angle2)
        R = draw_line_arc(left(R, angle), left(S, angle2))

    angle = angle2

    if cutout and offset == GAP:
        S = switches[68].position + rotate(vec_nm(0, half + GAP), angle2)
        draw_line(R, S)
        R = switches[69].position + vec_nm(0, half+offset)
        S = switches[72].position + vec_nm(0, half+offset)
        R = draw_line(R, S)
    else:
        S = switches[72].position + vec_nm(0, half+offset)
        R = draw_line_arc(right(R, angle), left(S))

    S = S + vec_nm(half+offset, -half-offset)
    R = draw_line_arc(right(R), down(S))

    S = switches[58].position + vec_nm(half+offset, half-offset)
    R = draw_line_arc(up(R), right(S))

    S = S + vec_nm(0, -half)
    R = draw_line_arc(left(R), down(S))

    S = switches[44].position + vec_nm(half+offset, half+offset)
    R = draw_line_arc(up(R), left(S))

    S = switches[15].position + vec_nm(half+offset, 0)
    R = draw_line_arc(right(R), down(S))

    S = switches[15].position + vec_nm(0, -half-offset)
    R = draw_line_arc(up(R), right(S))

    draw_line(R, RLeft)


def get_hexagon_params(D, W):
    """
    D = Flat-to-Flat Diameter (Hole width)
    W = Web Thickness (Metal between holes)
    """
    # 1. Fundamental Dimensions
    R = D / math.sqrt(3)  # Radius (Center to Vertex)
    s = R                 # Side length is equal to Radius

    # 2. Tiling Steps (Pitch)
    # Dx is the horizontal distance between centers in a row
    Dx = D + W

    # Dy is the vertical distance between rows in a staggered grid
    # Dy = Dx * sin(60 degrees)
    Dy = Dx * (math.sqrt(3) / 2)

    # 3. Vertices for Pointy-Top (Vertical) Hexagon centered at (0,0)
    # Ordered from Top Clockwise
    vertices = [
        vec_nm(0, int(nm(R))),                          # Top
        vec_nm(int(nm(D/2)), int(nm(R/2))),            # Top Right
        vec_nm(int(nm(D/2)), int(nm(-R/2))),           # Bottom Right
        vec_nm(0, int(nm(-R))),                         # Bottom
        vec_nm(int(nm(-D/2)), int(nm(-R/2))),          # Bottom Left
        vec_nm(int(nm(-D/2)), int(nm(R/2)))            # Top Left
    ]

    return {
        "R": R,
        "Dx": Dx,
        "Dy": Dy,
        "vertices": vertices
    }


def draw_hexagon_mesh():
    D, W = 3.5, 1.9
    params = get_hexagon_params(D, W)
    Dx = nm(params["Dx"])
    Dy = nm(params["Dy"])
    vertices = params["vertices"]

    def mid_pt(A, B):
        return midpoint(A, B)

    # hexagon using bezier curves
    def draw_hexagon(Orig):
        for (A, B) in zip(vertices, vertices[1:] + vertices[:1]):
            draw_line(Orig + A, Orig + B)
        # for (A, B, C) in zip(vertices, vertices[1:] + vertices[:1], vertices[2:] + vertices[:2]):
        #     draw_bezier(Orig + mid_pt(A, B), Orig + B, Orig + mid_pt(B, C), Orig + B)

    row = 0
    offset = vec_nm(nm(4.2), nm(-4.8))
    for i in range(1, SWITCH_COUNT+1):
        if i in [5, 6, 8, 9, 15, 16, 20, 24, 34, 35, 36, 38, 40, 50, 51, 62, 63, 64, 66, 67, 68, 70, 71, 72]:
            continue
        O = switches[i].position + offset
        if i >= 16:
            if not i in [22, 23, 30, 31, 39, 46, 49, 52, 53, 65]:
                draw_hexagon(O + vec_nm(int(Dx/2), -Dy))
        if i != 8:
            draw_hexagon(O + vec_nm(Dx, 0))
        draw_hexagon(O + vec_nm(int(Dx/2), Dy))
        draw_hexagon(O + vec_nm(int(1.5*Dx), Dy))
        draw_hexagon(O + vec_nm(0, int(2*Dy)))
        draw_hexagon(O + vec_nm(Dx, int(2*Dy)))
        if i in [45, 46, 59]:
            draw_hexagon(O + vec_nm(int(2.5 * Dx), -Dy))
            draw_hexagon(O + vec_nm(2*Dx, 0))
            if i != 59:
                draw_hexagon(O + vec_nm(int(2.5*Dx), Dy))
                draw_hexagon(O + vec_nm(2*Dx, int(2*Dy)))

    # holes in the empty space above last row
    O = switches[61].position + offset
    draw_hexagon(O + vec_nm(int(2.5*Dx), -Dy))
    draw_hexagon(O + vec_nm(int(2*Dx), 0))
    draw_hexagon(O + vec_nm(int(3*Dx), 0))
    draw_hexagon(O + vec_nm(int(2.5*Dx), Dy))

    O = switches[48].position + offset
    for i in range(1, 5):
        draw_hexagon(O + vec_nm(int((i-1.5)*Dx), int(3*Dy)))
        draw_hexagon(O + vec_nm(int((i-1)*Dx), int(4*Dy)))
        if i != 4:
            draw_hexagon(O + vec_nm(int((i+0.5)*Dx), int(5*Dy)))

    O = switches[49].position + offset
    for i in range(3):
        draw_hexagon(O + vec_nm(int((i+0.5)*Dx), int(3*Dy)))
        draw_hexagon(O + vec_nm(int((i+1)*Dx), int(4*Dy)))
        if i != 2:
            draw_hexagon(O + vec_nm(int((i+1.5)*Dx), int(5*Dy)))
        draw_hexagon(O + vec_nm(int((i+1)*Dx), int(6*Dy)))

    O = switches[65].position + offset
    for i in range(12):
        if i in [1, 3]:
            continue
        if not i in [1, 2, 8, 9]:
            draw_hexagon(O + vec_nm(int((i+2.5)*Dx), -Dy))
        if i != 9:
            draw_hexagon(O + vec_nm(int((i+2)*Dx), 0))
        if not i in [7, 8, 9]:
            draw_hexagon(O + vec_nm(int((i+2.5)*Dx), Dy))
        if i < 5:
            draw_hexagon(O + vec_nm(int((i+2)*Dx), int(2*Dy)))

    # Holes under battery compartment
    D, W = 3, 10
    params = get_hexagon_params(D, W)
    Dx = nm(params["Dx"])
    Dy = nm(params["Dy"])
    vertices = params["vertices"]

    O = vec_nm(nm(6), nm(120))
    for i in list(range(5)) + list(range(17, 22)):
        if i < 4 or (i > 10 and i < 31):
            draw_hexagon(O + vec_nm(int(i*Dx), Dy))
        if i != 24:
            draw_hexagon(O + vec_nm(int((i - 0.5)*Dx), int(2*Dy)))
        draw_hexagon(O + vec_nm(int(i*Dx), int(3*Dy)))
        if i > 0:
            draw_hexagon(O + vec_nm(int((i - 0.5)*Dx), int(4*Dy)))


def remove_border():
    """Remove border/helper graphics generated on the layers used by this script."""
    removable_layers = {
        BoardLayer.BL_Edge_Cuts,
        BoardLayer.BL_User_4,
        BoardLayer.BL_User_5,
        BoardLayer.BL_User_6,
        BoardLayer.BL_User_7,
        BoardLayer.BL_User_8,
    }
    old_shapes = [shape for shape in board.get_shapes() if shape.layer in removable_layers]
    if old_shapes:
        board.remove_items(old_shapes)


def projname() -> str:
    return Path(board.name).stem


def get_file_path() -> Path:
    """Return the Bezier CSV path next to the board when possible."""
    board_path = Path(board.name)
    if board_path.is_absolute():
        project_dir = board_path.parent
    else:
        project_dir = Path(os.getenv("KIPRJMOD", "."))
    return project_dir / CURVES_FILE


def save_bezier_curves():
    file_path = get_file_path()
    try:
        with file_path.open("w", newline="") as f:
            writer = csv.writer(f)
            for start, c1, c2, end in Bezier_Curves:
                writer.writerow([
                    start.x, start.y,
                    c1.x, c1.y,
                    c2.x, c2.y,
                    end.x, end.y,
                ])
        print(f"Saved {len(Bezier_Curves)} curves to {file_path}")
    except OSError as exc:
        print(f"Error saving {file_path}: {exc}")


def build_project_border(project: str):
    """Populate PENDING_SHAPES for the requested board variant."""
    global LAYER
    LAYER = BoardLayer.BL_Edge_Cuts

    if project == "pcb":
        draw_border(project)

    elif project == "swplate":
        draw_border_bezier(project, reveal=nm(0.2))
        draw_wrist_cavity()

        LAYER = BoardLayer.BL_User_4
        draw_border(project, offset=SIDE_WALL)
        draw_wrist()

        LAYER = BoardLayer.BL_User_5
        Bezier_Curves.clear()
        draw_border_bezier(project, reveal=0, usb_cutout=False, wire_cutout=True)
        draw_wrist_cavity()
        save_bezier_curves()

        LAYER = BoardLayer.BL_User_6
        draw_border(project, offset=GAP)

        LAYER = BoardLayer.BL_User_7
        draw_border(project, offset=GAP, cutout=True)
        draw_cutout_plate()

    elif project == "topcase":
        draw_border(project, offset=GAP, cutout=True)
        draw_border_bezier(project)
        draw_wrist_cavity()
        draw_cutout_plate()

        LAYER = BoardLayer.BL_User_6
        draw_border(project, offset=SIDE_WALL)
        draw_wrist()

    elif project == "botcase":
        draw_border(project, offset=GAP)
        draw_border_bezier(project)
        draw_wrist_cavity()

        LAYER = BoardLayer.BL_User_6
        draw_border(project, offset=SIDE_WALL)
        draw_wrist()

    elif project == "botcover":
        draw_border_bezier(project, reveal=nm(0.2))

        LAYER = BoardLayer.BL_User_5
        draw_hexagon_mesh()

        LAYER = BoardLayer.BL_User_6
        draw_border(project, offset=SIDE_WALL)
        draw_wrist()

    elif project == "wristrest":
        draw_border_bezier(project)

        LAYER = BoardLayer.BL_User_6
        draw_wrist_cavity()


def main():
    project = projname()
    supported = {"pcb", "swplate", "topcase", "botcase", "botcover", "wristrest"}
    if project not in supported:
        raise RuntimeError(f"Unrecognized project {project!r}")

    # Generate everything locally first.  No IPC writes happen during geometry construction.
    PENDING_SHAPES.clear()
    Bezier_Curves.clear()
    build_project_border(project)

    # Apply deletion + creation as one KiCad undo transaction.
    commit = board.begin_commit()
    try:
        remove_border()
        if PENDING_SHAPES:
            board.create_items(PENDING_SHAPES)
        board.push_commit(commit, f"Regenerate {project} border")
    except Exception:
        board.drop_commit(commit)
        raise

    print(f"Created {len(PENDING_SHAPES)} border shapes for {project}.")


if __name__ == "__main__":
    main()

