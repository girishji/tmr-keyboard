# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# KiCad Python script to save and restore component positions/orientations.
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())
#
# Using CSV file instead of ascii/binary pickle file, for readability

import pcbnew
import csv
import os
from typing import Dict, List, Tuple

# KiCad uses nanometers (nm) as its internal unit (IU)
# 1 mm = 1,000,000 nm
IU_PER_MM = pcbnew.IU_PER_MM

# --- Configuration ---
# File name for saving/loading footprint data
FOOTPRINT_FILE = "footprint_locations.csv"
# The list of reference prefixes to search for (R1, C1, J1, U1, etc.)
DEFAULT_PREFIXES = ["ADC", "R", "C", "D", "J", "U", "S", "H", "Hs", "LD", "USB"]


def get_file_path() -> str:
    """
    Constructs the absolute path to the CSV file, typically in the project directory.
    Assumes KiCad is running within a project context.
    """
    # KIPRJMOD points to the project directory if the board is saved.
    board_path = pcbnew.GetBoard().GetFileName()
    if board_path:
        project_dir = os.path.dirname(board_path)
    else:
        # Fallback if board is not saved, or using KIPRJMOD environment variable
        project_dir = os.getenv("KIPRJMOD", ".")

    # Ensure the path is correct
    return os.path.join(project_dir, FOOTPRINT_FILE)


def save_positions(prefixes: List[str] = DEFAULT_PREFIXES):
    """
    Saves the position (IU) and orientation (tenths of a degree) of all specified
    footprints to a CSV file.
    """
    board = pcbnew.GetBoard()

    # Header: Ref, PosX (IU), PosY (IU), Orientation (Tenths of a Degree)
    positions: Dict[str, Tuple[int, int, float]] = {}

    print("--- Saving Footprint Positions ---")

    # Iterate through all footprints on the board
    for fp in board.GetFootprints():
        ref = fp.GetReference()

        # Check if the reference matches any of the desired prefixes
        if any(ref.startswith(p) for p in prefixes):
            pos = fp.GetPosition()
            # KiCad uses tenths of a degree internally, but GetOrientationDegrees() is clearer
            angle = fp.GetOrientationDegrees()

            # Store data: (Ref, PosX, PosY, Angle)
            positions[ref] = (pos.x, pos.y, angle)

    file_path = get_file_path()

    try:
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            for ref, (x, y, angle) in positions.items():
                writer.writerow([ref, x, y, angle])
        print(f"✅ Successfully saved {len(positions)} footprints to:\n{file_path}")
    except IOError as e:
        print(f"❌ Error saving file at {file_path}: {e}")


def restore_position(ref_designator: str):
    """
    Reads the CSV and restores the position and orientation of a single footprint.
    """
    board = pcbnew.GetBoard()
    file_path = get_file_path()

    fp = board.FindFootprintByReference(ref_designator)
    if not fp:
        print(f"Footprint '{ref_designator}' not found on the board.")
        return

    try:
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == ref_designator:
                    # Data is stored as: Ref, PosX (IU), PosY (IU), Angle (Degrees)
                    try:
                        pos_x = int(row[1])
                        pos_y = int(row[2])
                        angle = float(row[3])

                        # Set Position using KiCad's internal VECTOR2I
                        fp.SetPosition(pcbnew.VECTOR2I(pos_x, pos_y))

                        # Set Orientation in degrees
                        fp.SetOrientationDegrees(angle)

                        print(f"✅ Restored {ref_designator}: Pos=({pos_x/IU_PER_MM:.2f}mm, {pos_y/IU_PER_MM:.2f}mm), Angle={angle:.2f}°")
                        pcbnew.Refresh()
                        return

                    except (ValueError, IndexError) as e:
                        print(f"❌ Error parsing data for {ref_designator} in CSV: {e}")
                        return

            print(f"Footprint '{ref_designator}' not found in the CSV file.")

    except FileNotFoundError:
        print(f"❌ Error: CSV file not found at {file_path}. Run 'save_positions()' first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def restore_all_positions():
    """
    Reads the CSV and restores the position and orientation of all stored footprints.
    """
    board = pcbnew.GetBoard()
    file_path = get_file_path()
    restored_count = 0

    try:
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 4:
                    continue

                ref = row[0]
                fp = board.FindFootprintByReference(ref)

                if fp:
                    try:
                        pos_x = int(row[1])
                        pos_y = int(row[2])
                        angle = float(row[3])

                        fp.SetPosition(pcbnew.VECTOR2I(pos_x, pos_y))
                        fp.SetOrientationDegrees(angle)
                        restored_count += 1

                    except (ValueError, IndexError):
                        print(f"Skipping {ref}: Bad data format in CSV.")

        print(f"--- Restored Footprint Positions ---")
        print(f"✅ Successfully restored positions for {restored_count} footprints.")
        pcbnew.Refresh()

    except FileNotFoundError:
        print(f"❌ Error: CSV file not found at {file_path}. Run 'save_positions()' first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Example ---

# 1. Save all current positions
# save_positions()

# 2. Restore a specific position (e.g., after moving it accidentally)
# restore_position("J1")

# 3. Restore all positions
# restore_all_positions()

print("\nScript loaded. Use save_positions(), restore_position('REF'), or restore_all_positions().")

