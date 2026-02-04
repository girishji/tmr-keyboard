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

import math
import pcbnew

# =============================================================================
# CONFIGURATION
# =============================================================================
KEY_SPACING = 19.00  # Standard key spacing in mm
SWITCH_COUNT = 72

IS_PCB_MOUNT = True  # Set to False for Plate generation
# IS_PCB_MOUNT = False

# Mounting Hole Coordinates (Layout specific)
# Format: (x_mm, y_mm)
HOLES_SMALL = [
    (-3.5, -2),
    (KEY_SPACING * 7.5, KEY_SPACING * 0.47),
    (KEY_SPACING * 14.5, KEY_SPACING * 0.47),
    (-3.5, KEY_SPACING * 4 + 2),
    (KEY_SPACING * 2.25, KEY_SPACING * 2.47),
    (KEY_SPACING * 7.25, KEY_SPACING * 2.47),
    # (KEY_SPACING * 4.545, KEY_SPACING * 4.4),
    (105, 75.5),
    (170, 75.5),
    # (KEY_SPACING * 9.955, KEY_SPACING * 4.4),
    (KEY_SPACING * 5, KEY_SPACING * 1.47),
    (KEY_SPACING * 11, KEY_SPACING * 1.47),
    (KEY_SPACING * 14.25 + 2, KEY_SPACING * 3.5 - 2),
    (KEY_SPACING * 13.5 - 1.25, KEY_SPACING * 2),
]

# HOLES_LARGE = [
#     (KEY_SPACING * 4.5, KEY_SPACING * 0.47),
#     (KEY_SPACING * 12.5, KEY_SPACING * 0.47),
#     (KEY_SPACING * 15.35, KEY_SPACING * 1.35),
#     (KEY_SPACING * 0.65, KEY_SPACING * .65),
#     (KEY_SPACING * 5.25, KEY_SPACING * 2.47),
#     (KEY_SPACING * 9.25, KEY_SPACING * 2.47),
#     (KEY_SPACING * 0.1, KEY_SPACING * 4.35),
#     (KEY_SPACING * 13.22, KEY_SPACING * 4.35),
# ]

COMPONENTS = [
    # ("M1", KEY_SPACING * 8.25 - 1, 4.4, 90, True),  # MCU module
    ("MDBT1", 161, -1.6, 180, True),  # MCU module
    ("MUXA1", 155.44, 12.27, 135, True),
    ("MUXA2", 167.22, 11.11, 0, True),
    # ("USB1", 3.4 + KEY_SPACING * 0.5, KEY_SPACING, -90, False),  # gct4515
    # ("USB1", 3.4 + KEY_SPACING * 0.5 - 1.2, KEY_SPACING, -90, False),  # gct4125
    ("Jusb1", -9, KEY_SPACING / 2, -90, False),  # gct4105 usb-c
    ("MUXB1", KEY_SPACING * 6.5, 4.5, 180, True),
    ("MUXB2", KEY_SPACING * 6, KEY_SPACING + 4.5, 180, True),
    ("MUXB3", KEY_SPACING * 6.25, KEY_SPACING * 2 + 4.5, 180, True),
    ("MUXB4", KEY_SPACING * 6.75 + 1.5, KEY_SPACING * 3 + 4.5, 180, True),
    ("MUXB5", KEY_SPACING * 9.5, 4.5, 0, True),
    ("MUXB6", KEY_SPACING * 10, KEY_SPACING + 4.5, 0, True),
    ("MUXB7", KEY_SPACING * 9.25, KEY_SPACING * 2 + 4.5, 180, True),
    ("MUXB8", KEY_SPACING * 7.75 + 0.25, KEY_SPACING * 3 + 4.5, 180, True),
    ("LEDDR1", KEY_SPACING * 7.25, 32.6, 180, True),
    # ("SW1", -3.1, KEY_SPACING * 3, 90, True),
    ("SW1", 21, 38, -90, True),  # Button switch
    ("PMIC1", KEY_SPACING * 1.875 - 1, KEY_SPACING, 180, True),
    ("JTAG1", 27.52, -4.89, 0, True),
    ("JTAG2", 5.7, 0.8, -90, True),
    ("BAT1", KEY_SPACING * (2 + 1/2 - 1/16), 80, 0, False),
    ("BAT2", KEY_SPACING * (12 + 1/16 + 1/32), 80, 0, False),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def mm_to_nm(mm_val):
    """Converts millimeters to KiCad internal units (nanometers)."""
    return pcbnew.FromMM(mm_val)


def set_position_mm(footprint, x_mm, y_mm):
    """Sets a footprint position using MM coordinates."""
    if footprint:
        footprint.SetPosition(pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm)))


def rotate_point(point, origin, angle_deg):
    """
    Rotate a VECTOR2I point around an origin by angle in degrees.
    Returns new VECTOR2I.
    """
    angle_rad = math.radians(angle_deg)

    # Translate to origin
    px = point.x - origin.x
    py = point.y - origin.y

    # Apply rotation matrix
    rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
    ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)

    # Translate back
    return pcbnew.VECTOR2I(int(origin.x + rx), int(origin.y + ry))


# =============================================================================
# LOGIC
# =============================================================================
def calculate_switch_positions():
    """
    Calculates the X, Y coordinates for all switches based on the layout logic.
    Returns a list of tuples (x, y) where index matches Switch Reference number.
    """
    # Initialize with dummy index 0
    positions = [(0, 0)] * (SWITCH_COUNT + 1)
    dim = KEY_SPACING

    # --- Row 1 ---
    for i in range(1, 16):
        positions[i] = (i * dim, 0)

    # --- Row 2 ---
    offs = dim + dim / 4
    positions[16] = (offs, dim)
    for i in range(17, 29):
        positions[i] = (offs + dim / 4 + (i - 16) * dim, dim)
    positions[29] = (offs + dim / 4 + dim * 13 + dim / 4, dim)

    # --- Row 3 ---
    offs = (1 - 1 / 4) * dim
    positions[30] = (offs - dim * 1 / 8, 2 * dim)
    for i in range(31, 42):
        positions[i] = (offs + (i - 30) * dim, 2 * dim)

    offs += 11 * dim
    positions[42] = (offs + (1 + 1/8) * dim, 2 * dim)

    offs += dim * (2 + 1/4)
    positions[43] = (offs, 2 * dim)

    offs += dim
    positions[44] = (offs, 2 * dim)

    # --- Row 4 ---
    offs = dim * (-1 / 2 - 1 / 8)
    positions[45] = (offs + dim, 3 * dim)

    offs += dim * (1 + 3 / 8 + 1 / 8)
    positions[46] = (offs + dim, 3 * dim) # 1.75u

    offs += dim * (3 / 8)
    for i in range(47, 57):
        positions[i] = (offs + (i - 45) * dim, 3 * dim)

    offs += dim * 12
    positions[57] = (offs + 3 / 8 * dim, 3 * dim) # 1.75u shift

    offs += dim * (1 + 3 / 4)
    positions[58] = (offs, 3 * dim)

    # --- Row 5 (Angled cluster) ---
    x_offset = 0.6  # Accommodate angled keys
    offs = (1 - 1 / 2 + 1 / 8) * dim - x_offset
    positions[59] = (offs, 4 * dim)
    positions[60] = (offs + dim * (1 + 1 / 4), 4 * dim)
    positions[61] = (offs + dim * (2 + 1 / 2 - 1 / 8), 4 * dim)

    offs = (3 + 1 / 2 + 1 / 8) * dim
    positions[62] = (offs + dim / 2 - 0.75, 4 * dim + 3.5)

    offs += dim * (1 + 1 / 4 + 1 / 8)
    positions[63] = (offs + 0.6, 4 * dim + 10)

    offs += dim
    positions[64] = (offs - 0.6, 4.5 * dim + 7)

    offs += dim * 1.25
    positions[65] = (offs, 4 * dim)

    positions[66] = (offs + dim + dim / 4 + 0.6, 4.5 * dim + 7)

    offs += dim * 1.25
    positions[67] = (offs + dim - 0.6, 4 * dim + 10)
    positions[68] = (offs + 2 * dim - 1.75, 4 * dim + 0 + 3.5)

    offs += 2 * dim + x_offset
    positions[69] = (offs + dim, 4 * dim)

    offs += (2 + 1 / 8) * dim
    positions[70] = (offs, 4 * dim)

    offs += (1 + 1 / 8) * dim
    positions[71] = (offs, 4 * dim)

    offs += dim
    positions[72] = (offs, 4 * dim)

    return positions


def place_switches_and_stabs(is_pcb):
    """Places switch footprints and associated stabilizers."""
    board = pcbnew.GetBoard()

    # Retrieve footprints. Indices 0 are unused/dummy.
    switches = [board.FindFootprintByReference(f'S{i}') for i in range(SWITCH_COUNT + 1)]
    # Assuming Stabilizers are Stb1, Stb2
    stabs = [board.FindFootprintByReference(f'Stb{i}') for i in range(3)]

    positions = calculate_switch_positions()

    # 1. Place standard orientation switches
    for i in range(1, SWITCH_COUNT + 1):
        if switches[i]:
            switches[i].SetOrientationDegrees(0)
            set_position_mm(switches[i], *positions[i])

    # 2. Handle Angled Keys (Bottom Row / Ergo Cluster)
    angle = 20

    # Specific rotations for layout
    if switches[62]: switches[62].SetOrientationDegrees(-angle)
    if switches[63]: switches[63].SetOrientationDegrees(-angle)

    # Complex Logic for Switch 64 & Stab 1
    if is_pcb:
        if switches[64]: switches[64].SetOrientationDegrees(-angle)
        if stabs[1]:
            set_position_mm(stabs[1], *positions[64])
            stabs[1].SetOrientationDegrees(-angle + 90)
    else:
        if switches[64]: switches[64].SetOrientationDegrees(-angle + 90)

    # Complex Logic for Switch 66 & Stab 2
    if is_pcb:
        if switches[66]: switches[66].SetOrientationDegrees(angle)
        if stabs[2]:
            set_position_mm(stabs[2], *positions[66])
            stabs[2].SetOrientationDegrees(angle - 90)
    else:
        if switches[66]: switches[66].SetOrientationDegrees(angle - 90)

    if switches[67]: switches[67].SetOrientationDegrees(angle)
    if switches[68]: switches[68].SetOrientationDegrees(angle)


def place_sw_components():
    """Places components relative to their parent switches."""
    board = pcbnew.GetBoard()

    # Offset relative to switch center (in mm)
    offset_mm = [
        ('TMR', (0, 4.4), 180),  # Sensor
        ('Cvout', (-2.8, 4.4), 90),  # Bypass cap
        ('Cvcc', (2.8, 4.4), -90),  # Bypass cap
        ('D', (0, -4.75), 0),  # LED
        ]

    for (sym, pos, rot_deg) in offset_mm:
        offset_vec = pcbnew.VECTOR2I(mm_to_nm(pos[0]), mm_to_nm(pos[1]))
        for i in range(1, SWITCH_COUNT + 1):
            if sym == 'Cvout' and i == 9:
                continue
            if sym == 'Cvcc' and i == 8:
                continue
            sw = board.FindFootprintByReference(f"S{i}")
            comp = board.FindFootprintByReference(f"{sym}{i}")

            if sw and comp:
                deg = sw.GetOrientationDegrees()
                sw_pos = sw.GetPosition()

                # Match rotation
                comp.SetOrientationDegrees(deg + rot_deg)

                # Compute position: Rotate the offset vector to match switch rotation
                new_pos = rotate_point(offset_vec + sw_pos, sw_pos, -deg)
                comp.SetPosition(new_pos)
                if comp.GetLayer() == pcbnew.F_Cu:
                    comp.Flip(new_pos, True)


def place_mounting_holes(is_pcb):
    """Places mounting holes based on global coordinates."""
    board = pcbnew.GetBoard()

    for i, (x, y) in enumerate(HOLES_SMALL):
        fp = board.FindFootprintByReference(f"Hs{i+1}")
        set_position_mm(fp, x, y)

    # Place Hs series (Small holes)
    # if is_pcb:
    #     for i, (x, y) in enumerate(HOLES_SMALL):
    #         fp = board.FindFootprintByReference(f"Hs{i+1}")
    #         set_position_mm(fp, x, y)

    # Place H series (Large holes)
    # for i, (x, y) in enumerate(HOLES_LARGE):
    #     fp = board.FindFootprintByReference(f"H{i+1}")
    #     set_position_mm(fp, x, y)


def place_components(is_pcb):
    """Places components."""
    board = pcbnew.GetBoard()

    for i, (fpname, x, y, deg, flip) in enumerate(COMPONENTS):
        if not is_pcb and fpname not in ['Jusb1', 'BAT1', 'BAT2']:
            continue
        fp = board.FindFootprintByReference(fpname)
        set_position_mm(fp, x, y)
        fp.SetOrientationDegrees(deg)
        if flip and fp.GetLayer() == pcbnew.F_Cu:
            fp.Flip(fp.GetPosition(), True)


def main():
    print(f"Starting placement... Mode: {'PCB' if IS_PCB_MOUNT else 'PLATE'}")

    place_switches_and_stabs(IS_PCB_MOUNT)
    if IS_PCB_MOUNT:
        place_sw_components()
    place_components(IS_PCB_MOUNT)
    place_mounting_holes(IS_PCB_MOUNT)

    pcbnew.Refresh()
    print("Placement complete.")
    # board.Save(board.GetFileName())


main()

