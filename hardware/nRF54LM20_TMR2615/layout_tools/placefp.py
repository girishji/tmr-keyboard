# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place footprints

"""Keyboard footprint placement for KiCad 10 IPC API.

All layout dimensions in this file are expressed in millimeters.
Conversion to KiCad's internal coordinate representation happens only when a
kipy Vector2 is created.

XXX:
KiCad 10 version does not perform the flip automatically. KiCad 10’s IPC API
has no working footprint-flip operation.
This script's intended behavior is:
1. Position and rotate footprints.
2. Select footprints that must move to B.Cu.
3. You press F once in PCB Editor to execute KiCad’s native flip.
The message is printed in the plugin output, but it may be easy to miss.

"""

import math
from pathlib import Path

from kipy import KiCad
from kipy.board_types import BoardLayer
from kipy.geometry import Angle, Vector2


# =============================================================================
# LAYOUT CONFIGURATION -- ALL DISTANCES ARE MILLIMETERS
# =============================================================================
KEY_SPACING_MM = 19.0
SWITCH_COUNT = 72

# PCB mounting screws: (x_mm, y_mm)
PCB_HOLES = [
    (KEY_SPACING_MM * 1.5, KEY_SPACING_MM * 0.45),
    (KEY_SPACING_MM * 7.5, KEY_SPACING_MM * 0.45),
    (KEY_SPACING_MM * 14.5, KEY_SPACING_MM * 0.45),
    (KEY_SPACING_MM * 1.125, KEY_SPACING_MM * 4 - 15),
    (KEY_SPACING_MM * 7.25, KEY_SPACING_MM * 2.47),
    (104, 70.5),
    (174, 72),
    (KEY_SPACING_MM * 5, KEY_SPACING_MM * 1.47),
    (KEY_SPACING_MM * 11, KEY_SPACING_MM * 1.47),
    (KEY_SPACING_MM * 14 + 2.35, KEY_SPACING_MM * 3),
]

# Housing screws: (x_mm, y_mm)
HOUSING_HOLES = [
    (3, 2.25),
    (104.5, -14.25),
    (199.5, -14.25),
    (291, -14.25),
    (-9.7, 71),
    (94.25, 102.25),
    (181.25, 102.25),
    (295, 61),
]

# Rivet holes: (x_mm, y_mm)
RIVET_HOLES = [
    (10, -12.5), (57, -12.5), (95, -12.5), (142.5, -12.5),
    (190, -12.5), (245, -12.5), (294, -12.5),   # top
    (309.5, 23), (308.5, 65.5),                 # right
    (-8, 39), (-9, 85),                         # left
    (62.75, 88.5), (116.5, 115.5), (137.75, 88), (159, 115.5),
    (213, 88.5), (265, 83),                     # bottom
    (24, 113), (-10, 130.5), (-10, 165), (30, 177),
    (70, 165.5), (56, 122),                     # left wrist rest
    (253, 113), (290.5, 130.5), (291, 165), (246, 177),
    (205.5, 165.5), (220, 122),                 # right wrist rest
]

# Dowels: (x_mm, y_mm)
DOWEL_HOLES = [
    (4.55, -4.45),
    (295, 52),
]

# Support screws for bottom cover: (x_mm, y_mm)
BOTTOM_SUPPORT_HOLES = [
    (99.75, 40.5),
    (213.75, 40.5),
]

# XXX: Keep synchronized with border.py if that file uses the same geometry.
WRIST_X_OFFSET_MM = 64
WRIST_Y_OFFSET_MM = 30  # XXX: Used to be 28
WRIST_X_LENGTH_MM = 88
WRIST_Y_LENGTH_MM = 65
WRIST_RIGHT_X_EXTRA_MM = 5

# (reference, x_mm, y_mm, orientation_degrees, flip_to_back_if_on_front)
COMPONENTS = [
    ("M1", 167.59, 4.2, 180, True),  # MCU module
    ("MUXA1", 154.7, 13.75, 180, True),
    ("MUXA2", 166.75, 9.5, 0, True),
    ("MUXB1", 122.5, 4.5, 180, True),
    ("MUXB2", 113, 23.5, 180, True),
    ("MUXB3", 117.5, 42.5, 180, True),
    ("MUXB4", 127, 61.5, 180, True),
    ("MUXB5", 178.75, 4.5, 180, True),
    ("MUXB6", 188.25, KEY_SPACING_MM + 4.5, 180, True),
    ("MUXB7", 174.25, 44.5, 180, True),
    ("MUXB8", 146, 63, 180, True),
    ("LEDDR1", 139.5, 32.0, 180, True),
    ("PMIC1", KEY_SPACING_MM * 1.875 - 1, KEY_SPACING_MM, 180, True),
    ("Jusb1", 19.5, -13.7, 180, False),  # USB receptacle
    ("SW1", 199.4, -2.52, 90, True),
    ("SW2", 15, 27.2, -90, True),
    ("JTAG1", 180.5, -3.5, -90, True),
    ("BAT1", 23 - KEY_SPACING_MM / 4, 79, 0, False),
    ("BAT2", 234, 79, 0, False),
]

# Components placed relative to each switch:
# (reference_prefix, (x_offset_mm, y_offset_mm), rotation_offset_degrees)
SWITCH_COMPONENTS = [
    ("TMR", (-1.5, 4.5 - 0.2), -90),
    ("Cvout", (-3.2, 4.1), 90),
    ("Cvcc", (-1.98, 6), 180),
    ("D", (0, -4.75), 0),
]

VALID_PROJECTS = {
    "pcb",
    "swplate",
    "topcase",
    "botcase",
    "botcover",
    "wristrest",
}


# =============================================================================
# IPC / GEOMETRY HELPERS
# =============================================================================
def mm(x_mm, y_mm):
    """Create a KiCad Vector2 from millimeter coordinates."""
    return Vector2.from_xy_mm(x_mm, y_mm)


def rotate_vector(vector, angle_deg):
    """Return *vector* rotated around (0, 0) by angle_deg."""
    angle = math.radians(angle_deg)
    c = math.cos(angle)
    s = math.sin(angle)

    return Vector2.from_xy(
        int(round(vector.x * c - vector.y * s)),
        int(round(vector.x * s + vector.y * c)),
    )


def project_name(board):
    """Return the PCB filename without its extension."""
    return Path(board.name).stem


class Placement:
    """Accumulate footprint changes locally and send them to KiCad together."""

    def __init__(self, board):
        self.board = board
        self.footprints = {
            fp.reference_field.text.value: fp
            for fp in board.get_footprints()
        }
        self.changed = {}
        self.flip_to_back = set()

    def get(self, reference):
        """Return a footprint by reference, or None if it is absent."""
        return self.footprints.get(reference)

    def require(self, reference):
        """Return a footprint by reference, raising a useful error if absent."""
        fp = self.get(reference)
        if fp is None:
            raise RuntimeError(f"Footprint {reference!r} not found")
        return fp

    def mark_changed(self, fp):
        if fp is not None:
            self.changed[fp.reference_field.text.value] = fp

    def set_position(self, reference_or_fp, x_mm, y_mm):
        fp = (
            self.get(reference_or_fp)
            if isinstance(reference_or_fp, str)
            else reference_or_fp
        )
        if fp is not None:
            fp.position = mm(x_mm, y_mm)
            self.mark_changed(fp)
        return fp

    def set_orientation(self, reference_or_fp, degrees):
        fp = (
            self.get(reference_or_fp)
            if isinstance(reference_or_fp, str)
            else reference_or_fp
        )
        if fp is not None:
            fp.orientation = Angle.from_degrees(degrees)
            self.mark_changed(fp)
        return fp

    def place(self, reference, x_mm, y_mm, degrees=None):
        fp = self.get(reference)
        if fp is None:
            return None

        fp.position = mm(x_mm, y_mm)
        if degrees is not None:
            fp.orientation = Angle.from_degrees(degrees)
        self.mark_changed(fp)
        return fp

    def request_back_side(self, fp):
        """Flip fp to B.Cu later, but only if it is currently on F.Cu."""
        if fp is not None and fp.layer == BoardLayer.BL_F_Cu:
            self.flip_to_back.add(fp.reference_field.text.value)

    def apply(self):
        """Send all accumulated changes to the PCB editor as one undoable edit."""
        if not self.changed and not self.flip_to_back:
            return

        commit = self.board.begin_commit()

        try:
            if self.changed:
                self.board.update_items(list(self.changed.values()))

            # KiCad 10's IPC API has no footprint-flip operation. Assigning
            # FootprintInstance.layer is not a valid substitute because it
            # does not correctly mirror all footprint children. Newer API
            # versions provide Board.flip_items(), so use it when available
            # and fall back to a manual native flip on KiCad 10.
            to_flip = [
                self.footprints[ref]
                for ref in self.flip_to_back
                if ref in self.footprints
            ]

            manual_flip = []
            if to_flip:
                flip_items = getattr(self.board, "flip_items", None)
                if flip_items is not None:
                    flip_items(to_flip)
                else:
                    manual_flip = to_flip

            self.board.push_commit(commit, "Place keyboard footprints")

        except Exception:
            self.board.drop_commit(commit)
            raise

        if manual_flip:
            # Select only the still-front-side footprints. Pressing F once in
            # PCB Editor performs KiCad's native, complete footprint flip.
            self.board.clear_selection()
            self.board.add_to_selection(manual_flip)
            refs = ", ".join(
                sorted(fp.reference_field.text.value for fp in manual_flip)
            )
            print(
                "KiCad 10 placed the footprints but its IPC API cannot flip "
                "them. The required footprints are selected in PCB Editor. "
                f"Press F once to flip them to B.Cu: {refs}",
                flush=True,
            )


# =============================================================================
# SWITCH LAYOUT
# =============================================================================
def calculate_switch_positions():
    """Return switch positions in mm, indexed by switch number (1..72)."""
    p = [(0.0, 0.0)] * (SWITCH_COUNT + 1)
    d = KEY_SPACING_MM

    # Row 1
    for i in range(1, 16):
        p[i] = (i * d, 0)

    # Row 2
    x = d + d / 4
    p[16] = (x, d)
    for i in range(17, 29):
        p[i] = (x + d / 4 + (i - 16) * d, d)
    p[29] = (x + d / 4 + 13 * d + d / 4, d)

    # Row 3
    x = 0.75 * d
    p[30] = (x - d / 8, 2 * d)
    for i in range(31, 42):
        p[i] = (x + (i - 30) * d, 2 * d)

    x += (12 + 1 / 8) * d
    p[42] = (x, 2 * d)
    x += (1 + 1 / 8) * d
    p[43] = (x, 2 * d)
    x += d
    p[44] = (x, 2 * d)

    # Row 4
    x = d * (-1 / 2 + 1 / 8 - 1 / 4)
    p[45] = (x + d, 3 * d)

    x += d * (1 + 3 / 8 + 1 / 8)
    p[46] = (x + d, 3 * d)  # 1.75u

    x += d * 3 / 8
    for i in range(47, 57):
        p[i] = (x + (i - 45) * d, 3 * d)

    x += d * (11 + 1 / 4)
    p[57] = (x + d, 3 * d)  # 1.5u shift

    x += d * (1 + 1 / 4)
    p[58] = (x + d, 3 * d)

    # Row 5 -- angled thumb/ergo cluster
    x_offset = d / 4
    x = (1 - 1 / 2 + 1 / 8) * d - x_offset
    p[59] = (x, 4 * d)
    p[60] = (x + d * (1 + 1 / 4), 4 * d)
    p[61] = (x + d * (2 + 1 / 2 - 1 / 8), 4 * d)

    x = (3 + 1 / 2 + 1 / 8) * d
    p[62] = (x + d / 2 - 1.15, 4 * d + 4.7)

    x += d * (1 + 1 / 4 + 1 / 8)
    p[63] = (95.88, 84.96)

    x += d
    p[64] = (x - 0.6, 4.5 * d + 7)

    x += d * 1.25
    p[65] = (x, 4 * d)
    p[66] = (x + d + d / 4 + 0.6, 4.5 * d + 7)

    x += d * 1.25
    p[67] = (x + d - 0.1, 4 * d + 11.25)
    p[68] = (x + 2 * d - 1.15, 4 * d + 4.7)

    x += 3 * d + x_offset
    p[69] = (x, 4 * d)
    x += 1.125 * d
    p[70] = (x, 4 * d)
    x += 1.125 * d
    p[71] = (x, 4 * d)
    x += d
    p[72] = (x, 4 * d)

    return p


def place_switches_and_stabilizers(layout, is_pcb):
    positions = calculate_switch_positions()

    # Start every switch at 0 degrees.
    for i in range(1, SWITCH_COUNT + 1):
        x, y = positions[i]
        layout.place(f"S{i}", x, y, 0)

    angle = 20
    special_angles = {
        62: -angle,
        63: -angle + 90,
        64: -angle + 90,
        66: angle - 90,
        67: angle,
        68: angle,
    }
    for switch_number, degrees in special_angles.items():
        layout.set_orientation(f"S{switch_number}", degrees)

    if is_pcb:
        layout.place("Stb1", *positions[64], -angle + 90)
        layout.place("Stb2", *positions[66], angle - 90)


def place_switch_components(layout):
    """Place TMR sensors, capacitors and LEDs relative to their switches."""
    for prefix, (dx_mm, dy_mm), rotation_offset in SWITCH_COMPONENTS:
        local_offset = mm(dx_mm, dy_mm)

        for i in range(1, SWITCH_COUNT + 1):
            if i == 9:
                continue

            switch = layout.get(f"S{i}")
            component = layout.get(f"{prefix}{i}")
            if switch is None or component is None:
                continue

            switch_angle = switch.orientation.degrees

            # Keep the sign convention from the original SWIG script:
            # component offset is rotated by -switch_angle.
            rotated_offset = rotate_vector(local_offset, -switch_angle)
            component.position = switch.position + rotated_offset
            component.orientation = Angle.from_degrees(
                switch_angle + rotation_offset
            )

            layout.mark_changed(component)
            layout.request_back_side(component)


# =============================================================================
# WRIST REST / HOLES
# =============================================================================
def wrist_rest_corners(layout):
    """Return L1..L4, R1..R4 as KiCad Vector2 positions."""
    s65 = layout.require("S65")

    anchor = s65.position + mm(0, KEY_SPACING_MM / 2)

    left_x1 = -(WRIST_X_OFFSET_MM + WRIST_X_LENGTH_MM)
    left_x2 = -WRIST_X_OFFSET_MM
    right_x1 = WRIST_X_OFFSET_MM + WRIST_X_LENGTH_MM + WRIST_RIGHT_X_EXTRA_MM
    right_x2 = WRIST_X_OFFSET_MM
    top_y = WRIST_Y_OFFSET_MM
    bottom_y = WRIST_Y_OFFSET_MM + WRIST_Y_LENGTH_MM

    l1 = anchor + mm(left_x1, top_y)
    l2 = anchor + mm(left_x2, top_y)
    l3 = anchor + mm(left_x2, bottom_y)
    l4 = anchor + mm(left_x1, bottom_y)

    r1 = anchor + mm(right_x1, top_y)
    r2 = anchor + mm(right_x2, top_y)
    r3 = anchor + mm(right_x2, bottom_y)
    r4 = anchor + mm(right_x1, bottom_y)

    return l1, l2, l3, l4, r1, r2, r3, r4


def place_hole_series(layout, prefix, coordinates):
    for i, (x_mm, y_mm) in enumerate(coordinates, start=1):
        layout.set_position(f"{prefix}{i}", x_mm, y_mm)


def set_vector_position(layout, reference, position):
    """Set an already-computed Vector2 position."""
    fp = layout.get(reference)
    if fp is not None:
        fp.position = position
        layout.mark_changed(fp)


def place_mounting_holes(layout, is_pcb):
    place_hole_series(layout, "Hs", PCB_HOLES)
    place_hole_series(layout, "H", HOUSING_HOLES)
    place_hole_series(layout, "Hd", DOWEL_HOLES)
    place_hole_series(layout, "Hr", RIVET_HOLES)
    place_hole_series(layout, "Hm", BOTTOM_SUPPORT_HOLES)

    if is_pcb:
        return

    l1, l2, l3, l4, r1, r2, r3, r4 = wrist_rest_corners(layout)
    d = 8

    wrist_holes = {
        "H9": l1 + mm(d, d),
        "H10": l2 + mm(-d, 15.5),
        "H11": l3 + mm(-d, -d),
        "H12": l4 + mm(d, -d),
        "H13": r1 + mm(-d, d),
        "H14": r2 + mm(d, 15.5),
        "H15": r3 + mm(d, -d),
        "H16": r4 + mm(-d, -d),
    }

    for reference, position in wrist_holes.items():
        set_vector_position(layout, reference, position)


# =============================================================================
# FIXED COMPONENTS
# =============================================================================
def place_fixed_components(layout, is_pcb):
    non_pcb_components = {"Jusb1", "SW1", "SW2", "M1"}

    for reference, x_mm, y_mm, degrees, flip in COMPONENTS:
        if not is_pcb and reference not in non_pcb_components:
            continue

        fp = layout.place(reference, x_mm, y_mm, degrees)
        if flip:
            layout.request_back_side(fp)


# =============================================================================
# MAIN
# =============================================================================
def main():
    board = KiCad().get_board()
    project = project_name(board)

    if project not in VALID_PROJECTS:
        print(f"Error: unrecognized project {project!r}", flush=True)
        return

    layout = Placement(board)

    if project == "pcb":
        place_switches_and_stabilizers(layout, is_pcb=True)
        place_switch_components(layout)
        place_fixed_components(layout, is_pcb=True)
        place_mounting_holes(layout, is_pcb=True)

    elif project in {"swplate", "botcase", "botcover"}:
        place_switches_and_stabilizers(layout, is_pcb=False)
        place_fixed_components(layout, is_pcb=False)
        place_mounting_holes(layout, is_pcb=False)

    elif project in {"topcase", "wristrest"}:
        place_switches_and_stabilizers(layout, is_pcb=False)
        place_mounting_holes(layout, is_pcb=False)

    layout.apply()
    print("Placement complete.", flush=True)


if __name__ == "__main__":
    main()
