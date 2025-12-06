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

import itertools
import math
import pcbnew
from pcbnew import VECTOR2I

dim = 19.00
COUNT = 72

def flip_footprint_to_back(footprint_ref):
    """
    Flips a specified footprint from the front (F.Cu) to the back (B.Cu) layer.
    """

    board = pcbnew.GetBoard()

    # Find the footprint by its reference designator (string)
    footprint = board.FindFootprintByRef(footprint_ref)
    if not footprint:
        print(f"Error: Footprint '{footprint_ref}' not found.")
        return

    current_layer = footprint.GetLayerName()
    if current_layer == "B.Cu":
        return

    if footprint.GetLayer() == pcbnew.F_Cu:
        footprint.SetLayer(pcbnew.B_Cu)


def sw_position():

    swpos = [(0, 0)] * (COUNT + 1)

    # row 1
    for i in range(1, 16):
        swpos[i] = (i * dim, 0)

    # row 2
    offs = dim + dim / 4
    swpos[16] = (offs, dim)
    for i in range(17, 29):
        swpos[i] = (offs + dim / 4 + (i - 16) * dim, dim)
    swpos[29] = (offs + dim / 4 + dim * 13 + dim / 4, dim)

    # row 3
    offs = (1 - 1 / 4) * dim
    swpos[30] = (offs - dim * 1 / 8, 2 * dim)
    for i in range(31, 42):
        swpos[i] = (offs + (i - 30) * dim, 2 * dim)
    offs += 11 * dim
    swpos[42] = (offs + (1 + 1/8) * dim, 2 * dim)
    offs += dim * (2 + 1/4)
    swpos[43] = (offs, 2 * dim)
    offs += dim
    swpos[44] = (offs, 2 * dim)

    # row 4
    offs = dim * (-1 / 2 - 1 / 8)
    swpos[45] = (offs + dim, 3 * dim)
    offs += dim * (1 + 3 / 8 + 1 / 8)
    swpos[46] = (offs + dim, 3 * dim) # 1.75u
    offs += dim * (3 / 8)
    for i in range(47, 57):
        swpos[i] = (offs + (i - 45) * dim, 3 * dim)
    offs += dim * 12
    swpos[57] = (offs + 3 / 8 * dim, 3 * dim) # 1.75u shift
    offs += dim * (1 + 3 / 4)
    swpos[58] = (offs, 3 * dim)

    # row 5
    x_offset = 0.6 # to accommodate for angled keys
    offs = (1 - 1 / 2 + 1 / 8) * dim - x_offset
    swpos[59] = (offs, 4 * dim)
    swpos[60] = (offs + dim * (1 + 1 / 4), 4 * dim)
    swpos[61] = (offs + dim * (2 + 1 / 2 - 1 / 8), 4 * dim)

    offs = (3 + 1 / 2 + 1 / 8) * dim
    swpos[62] = (offs + dim / 2 - 0.75, 4 * dim + 3.5)

    offs += dim * (1 + 1 / 4 + 1 / 8)
    swpos[63] = (offs + 0.6, 4 * dim + 10)

    offs += dim
    pos64 = (offs - 0.6, 4.5 * dim + 7)
    swpos[64] = pos64

    offs += dim * 1.25
    swpos[65] = (offs, 4 * dim)

    pos66 = (offs + dim + dim / 4 + 0.6, 4.5 * dim + 7)
    swpos[66] = pos66

    offs += dim * 1.25
    swpos[67] = (offs + dim - 0.6, 4 * dim + 10)
    swpos[68] = (offs + 2 * dim - 1.75, 4 * dim + 0 + 3.5)

    offs += 2 * dim + x_offset
    swpos[69] = (offs + dim, 4 * dim)

    offs += (2 + 1 / 8) * dim
    swpos[70] = (offs, 4 * dim)
    offs += (1 + 1 / 8) * dim
    swpos[71] = (offs, 4 * dim)
    offs += dim
    swpos[72] = (offs, 4 * dim)
    return swpos


def place_switches(ispcb):

    def place(fp, offset):
        x, y = offset
        fp.SetPosition(VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))

    def orient(fp, deg):
        fp.SetOrientationDegrees(deg)

    board = pcbnew.GetBoard()
    switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]
    stabs = [board.FindFootprintByReference('Stb' + str(num)) for num in range(2 + 1)]
    swpos = sw_position()

    for i in range(1, COUNT + 1):
        orient(switches[i], 0)
        place(switches[i], swpos[i])

    # orient the last row switches, and place stabs
    angle = 20
    orient(switches[62], -angle)
    orient(switches[63], -angle)
    if ispcb:
        orient(switches[64], -angle)
        place(stabs[1], swpos[64])
        orient(stabs[1], -angle + 90)
    else:
        orient(switches[64], -angle + 90)

    if ispcb:
        orient(switches[66], angle)
        place(stabs[2], swpos[66])
        orient(stabs[2], angle - 90)
    else:
        orient(switches[66], angle - 90)

    orient(switches[67], angle)
    orient(switches[68], angle)


def rotate_point(point, origin, angle_deg):
    """Rotate a VECTOR2I point around origin by angle in degrees."""
    angle_rad = math.radians(angle_deg)

    # Translate to origin
    px = point.x - origin.x
    py = point.y - origin.y

    # Apply rotation matrix
    rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
    ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)

    # Translate back and return as VECTOR2I
    return pcbnew.VECTOR2I(int(origin.x + rx), int(origin.y + ry))


def place_leds():
    board = pcbnew.GetBoard()

    switches = [
        board.FindFootprintByReference(f"S{num}")
        for num in range(COUNT + 1)
    ]

    leds = [
        board.FindFootprintByReference(f"D{num}")
        for num in range(1, COUNT + 1)
    ]

    # Create VECTOR2I offset in internal units (nm)
    offset = pcbnew.VECTOR2I(
        pcbnew.FromMM(0),
        pcbnew.FromMM(-dim * 0.25)
    )

    if any(leds):
        for led, sw in zip(leds, switches[1:]):
            deg = sw.GetOrientationDegrees()
            # Match LED rotation with switch
            led.SetOrientationDegrees(deg)
            swpos = sw.GetPosition()
            # Compute rotated position
            newpos = rotate_point(offset + swpos, swpos, -deg)
            led.SetPosition(newpos)


def place_mounting_holes_pcb():

    posHs = [
        (dim * 1.5, dim * 0.47),
        (dim * 7.5, dim * 0.47),
        (dim * 14.5, dim * 0.47),
        (dim * .1, dim * 4),
        (dim * 3.25, dim * 2.47),
        (dim * 7.25, dim * 2.47),
        (dim * 4.545, dim * 4.4),
        (dim * 9.955, dim * 4.4),
        (dim * 11, dim * 1.47),
        (dim * 14.5, dim * 3.47),
        ]

    posH = [
        (dim * 4.5, dim * .47),
        (dim * 12.5, dim * .47),
        (dim * 15.35, dim * 1.35),
        (dim * .65, dim * 1.35),
        (dim * 5.25, dim * 2.47),
        (dim * 9.25, dim * 2.47),
        (dim * .1, dim * 4.35),
        (dim * 13.22, dim * 4.35),
        ]

    board = pcbnew.GetBoard()

    holes = [board.FindFootprintByReference(f"Hs{num+1}") for num in range(len(posHs))]
    for fp, (x, y) in zip(holes, posHs):
        if fp:
            fp.SetPosition(VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))

    holes = [board.FindFootprintByReference(f"H{num+1}") for num in range(len(posH))]
    for fp, (x, y) in zip(holes, posH):
        if fp:
            fp.SetPosition(VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))


# PCB = False  # Plate, not pcb
PCB = True

place_switches(PCB)
place_leds()
if PCB:
    place_mounting_holes_pcb()

pcbnew.Refresh()
# board.Save(board.GetFileName())
