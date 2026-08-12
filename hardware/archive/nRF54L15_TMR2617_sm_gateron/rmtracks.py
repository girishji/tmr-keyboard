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

import pcbnew

def remove_tracks():
    # delete tracks and vias
    board = pcbnew.GetBoard()
    for t in board.GetTracks():
        board.Delete(t)
    pcbnew.Refresh()

remove_tracks()

# # 1. Get the currently loaded board object
# board = pcbnew.GetBoard()

# # 2. Prepare a list to hold all tracks and vias to be deleted
# elements_to_delete = []

# # 3. Iterate through all items on the board
# for item in board.Get = ():
#     # Check if the item is a track segment (pcbnew.TRACK is the base class for tracks/traces)
#     if isinstance(item, pcbnew.TRACK):
#         elements_to_delete.append(item)

#     # Check if the item is a via (pcbnew.VIA is the base class for vias)
#     elif isinstance(item, pcbnew.VIA):
#         elements_to_delete.append(item)

# # 4. Iterate through the prepared list and delete the elements
# count = 0
# for element in elements_to_delete:
#     board.Delete(element)
#     count += 1

# # 5. Print a confirmation message
# print(f"✅ Script executed successfully.")
# print(f"Removed {count} tracks and vias from the board.")
