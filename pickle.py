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

# https://deskthority.net/viewtopic.php?t=20144

# Use CSV file instead of ascii/binary pickle file, for readability

import pcbnew
from pcbnew import wxPoint, wxPointMM
import csv
import os


def write_csv():
    def coord(fp):
        pos = fp.GetPosition()
        angle = fp.GetOrientation()
        return pos.x, pos.y, angle

    board = pcbnew.GetBoard()
    positions = {
        sym + str(num): coord(board.FindFootprintByReference(sym + str(num)))
        for sym in ["R", "C", "J", "U"]
        for num in range(1, 1000)
        if board.FindFootprintByReference(sym + str(num))
    }

    with open(os.getenv("KIPRJMOD", "") + "/fplocations.csv", "w") as f:
        print(f.name)
        writer = csv.writer(f)
        for k, v in positions.items():
            writer.writerow([k, v[0], v[1], v[2]])


def read_csv():
    with open(os.getenv("KIPRJMOD", "") + "/fplocations.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            print(", ".join(row))


# pickle8r.placefp("J1")
def placefp(sym):
    with open(os.getenv("KIPRJMOD", "") + "/../pcb/fplocations.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == sym:
                board = pcbnew.GetBoard()
                fp = board.FindFootprintByReference(sym)
                pos = wxPoint(int(row[1]), int(row[2]))
                fp.SetPosition(pos)
                fp.SetOrientation(float(row[3]))
                pcbnew.Refresh()
                return


write_csv()
read_csv()
