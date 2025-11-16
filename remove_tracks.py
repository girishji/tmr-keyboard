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

import pcbnew

def remove_tracks():
    # delete tracks and vias
    board = pcbnew.GetBoard()
    for t in board.GetTracks():
        board.Delete(t)
    pcbnew.Refresh()

remove_tracks()
