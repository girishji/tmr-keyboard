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
from pcbnew import VECTOR2I, wxPoint, wxPointMM

dim = 19.00
COUNT = 72
board = pcbnew.GetBoard()

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]

def place_switches():

    def place(fp, offset):
        pointMM = wxPointMM(*offset)
        fp.SetPosition(VECTOR2I(pointMM.x, pointMM.y))

    orient = lambda fp, deg: fp.SetOrientationDegrees(deg)

    for i in range(1, COUNT + 1):
        orient(switches[i], 0)

    # row 1
    place(switches[1], (dim, 0))
    for i in range(2, 16):
        place(switches[i], (i * dim, 0))

    # row 2
    offs = dim + dim / 4
    place(switches[16], (offs, dim))
    for i in range(17, 29):
        place(switches[i], (offs + dim / 4 + (i - 16) * dim, dim))
    place(switches[29], (offs + dim / 4 + dim * 13 + dim / 4, dim))

    # row 3
    offs = (1 - 1 / 4) * dim
    place(switches[30], (offs - dim * 1 / 8, 2 * dim))
    for i in range(31, 42):
        place(switches[i], (offs + (i - 30) * dim, 2 * dim))
    offs += 11 * dim
    place(switches[42], (offs + (1 + 1/8) * dim, 2 * dim))
    offs += dim * (2 + 1/4)
    place(switches[43], (offs, 2 * dim))
    offs += dim
    place(switches[44], (offs, 2 * dim))

    # row 4
    offs = dim * (-1 / 2 - 1 / 8)
    place(switches[45], (offs + dim, 3 * dim))
    offs += dim * (1 + 3 / 8 + 1 / 8)
    place(switches[46], (offs + dim, 3 * dim)) # 1.75u
    offs += dim * (3 / 8)
    for i in range(47, 57):
        place(switches[i], (offs + (i - 45) * dim, 3 * dim))
    offs += dim * 12
    place(switches[57], (offs + 3 / 8 * dim, 3 * dim)) # 1.75u shift
    offs += dim * (1 + 3 / 4)
    place(switches[58], (offs, 3 * dim))

    # row 5
    offs = (1 - 1 / 2 - 1 / 8) * dim
    place(switches[59], (offs, 4 * dim))
    place(switches[60], (offs + dim * (1 + 1 / 4), 4 * dim))
    place(switches[61], (offs + dim * (2 + 1 / 4 + 1 / 8), 4 * dim))
    offs = (3 + 1 / 2 + 1 / 8) * dim
    place(switches[62], (offs + dim / 4 + 0.7, 4 * dim + 1))
    orient(switches[62], -5)
    # place(switches[62], (offs + dim / 4, 4 * dim))

    # rotated
    offs += dim * (1 + 1 / 4 + 1 / 8)
    place(switches[63], (offs + 1.35, 4 * dim + 7.8))
    orient(switches[63], -20 + 90)
    offs += dim

    place(switches[64], (offs - 0.6, 4.5 * dim + 7))
    orient(switches[64], -20 + 90)

    offs += dim * 1.25
    place(switches[65], (offs, 4 * dim))

    place(switches[66], (offs + dim + dim / 4 + 0.6, 4.5 * dim + 7))
    orient(switches[66], 20 + 90 + 180)
    offs += dim * 1.25
    place(switches[67], (offs + dim - 0.6, 4 * dim + 10))
    orient(switches[67], 20)
    place(switches[68], (offs + 2 * dim - 0.7, 4 * dim + 1))
    orient(switches[68], 5)
    #
    # place(switches[66], (offs + dim + dim / 4 + 0.0, 4.5 * dim + 5))
    # orient(switches[66], 18 + 90 + 180)
    # offs += dim * 1.25
    # place(switches[67], (offs + dim - 1, 4 * dim + 8.8))
    # orient(switches[67], 18)
    # place(switches[68], (offs + 2 * dim - 2, 4 * dim + 3))
    # orient(switches[68], 18)
    #
    # place(switches[68], (offs + 2 * dim, 4 * dim))
    #
    offs += 2 * dim
    place(switches[69], (offs + dim, 4 * dim))

    offs += (2 + 1 / 8) * dim
    place(switches[70], (offs, 4 * dim))
    offs += (1 + 1 / 8) * dim
    place(switches[71], (offs, 4 * dim))
    offs += dim
    place(switches[72], (offs, 4 * dim))


def transform(pt, around, theta):
    """
    Rotate vector 'pt' by 'theta' degrees. Add vector 'around' to vector 'pt'.
    """
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


def place_leds():
    leds = [board.FindFootprintByReference('D' + str(num)) for num in range(1, COUNT + 1)]
    offset = wxPointMM(0, -dim * 0.268)
    if any(leds):
        for led, sw in zip(leds, switches[1:]):
            deg = sw.GetOrientationDegrees()
            led.SetOrientationDegrees(deg)
            swpos = sw.GetPosition().getWxPoint()
            led.SetPosition(VECTOR2I(transform(offset, swpos, -deg)))

def place_ir_resistors():
    rIR = [board.FindFootprintByReference('Ri' + str(num)) for num in range(COUNT // 3 + 1)]
    if any(rIR):
        selected = itertools.chain(range(3, 28, 3), [29], range(32, 45, 3), range(47, 57, 3), [58, 61, 64, 67, 70])
        for i, j in zip(range(1, COUNT // 3 + 1), selected):
            offset = wxPointMM(dim * 0.415, -2.3) if i < 5 else wxPointMM(dim * 0.43, 0)
            deg = switches[j].GetOrientationDegrees()
            rIR[i].SetOrientationDegrees(deg + 90)
            swpos = switches[j].GetPosition().getWxPoint()
            rIR[i].SetPosition(VECTOR2I(transform(offset, swpos, -deg)))

def place_bjts():
    cols = 15
    bjt = [board.FindFootprintByReference('Q' + str(num)) for num in range(1, cols + 1)]
    if any(bjt):
        r1r = [board.FindFootprintByReference('R1_r' + str(num)) for num in range(1, cols + 1)]
        r2r = [board.FindFootprintByReference('R2_r' + str(num)) for num in range(1, cols + 1)]
        xoffset = -dim * .48
        yoffset = 2.8
        for bj, r1, r2, sw in zip(bjt, r1r, r2r, switches[1:]):
            bj.SetOrientationDegrees(-90)
            r1.SetOrientationDegrees(180)
            r2.SetOrientationDegrees(180)
            swpos = sw.GetPosition().getWxPoint()
            bj.SetPosition(VECTOR2I(transform(wxPointMM(xoffset, -1.3 + yoffset), swpos, 0)))
            r1.SetPosition(VECTOR2I(transform(wxPointMM(xoffset + .3, -4.1 + yoffset), swpos, 0)))
            r2.SetPosition(VECTOR2I(transform(wxPointMM(xoffset, 1.5 + yoffset), swpos, 0)))

def place_mounting_holes():
    delta = 0.6
    border = 0
    board = pcbnew.GetBoard()

    pos = [
            (0, -dim * 0.4 - border + delta),
            (-dim * 0.5, dim * 2),
            (-dim * 0.4, dim * 4.2 + border - delta),
            (dim * 2.5, -dim * 0.5 - border + delta),
            (dim * 6.5, -dim * 0.5 - border + delta),
            (dim * 10.5, -dim * 0.5 - border + delta),
            (dim * 14.5, -dim * 0.5 - border + delta),
            (dim * (2 - 1 / 8), dim * 1.5 - 2),
            (dim * 5, dim * 1.5 - delta),
            (dim * 9, dim * 1.5 - delta),
            (dim * 12, dim * 1.5 - delta),
            (dim * 7.25, dim * 2.5 - delta),
            (dim * (3.5 - 1 / 8) - 0.5, dim * 3.55 + delta),
            # (dim * 3.3 - 0.25, dim * 3.55 + delta),
            (dim * 11.75, dim * 3.436 + delta),
            (dim * 15.35, dim * 1.5 - border),
            (dim * 15.25, dim * 4.25 + border - 3 * delta),
            # (dim * 5.45, dim * 4.6 + border),
            # (dim * 8.85, dim * 4.25),
            (dim * 5.75, dim * 5.5),
            (dim * 8.75, dim * 5.5),
            ]

    holes = [board.FindFootprintByReference("Hs" + str(num + 1)) for num in range(0, len(pos))]
    if any(holes):
        for i, hole in enumerate(holes):
            hole.SetPosition(VECTOR2I(wxPointMM(*pos[i])))



place_switches()
# place_leds()
# place_ir_resistors()
# place_bjts()
# place_mounting_holes()

pcbnew.Refresh()
