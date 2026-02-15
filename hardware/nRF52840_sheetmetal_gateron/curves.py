# Write all Bezier curves points (start, control1, control2, end) into a CSV file.
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/9.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew
import csv
import os

CURVES_FILE = "curves.csv"


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
            for s, c1, c2, e in curves:
                writer.writerow([s.x, s.y, c1.x, c2.y, e.x, e.y])
        print(f"Successfully saved {len(curves)} curves to {file_path}")
    except IOError as e:
        print(f"Error saving file at {file_path}: {e}")



