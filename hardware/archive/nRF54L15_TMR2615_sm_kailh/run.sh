#!/bin/sh

# run this script in virtual env where build123d is installed

KICAD_PYTHON=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3

# extract edge cuts geometry into a json file
$KICAD_PYTHON export_edge_cuts.py ./botcover/botcover.kicad_pcb

# use build123d to recreate the geometry and export STEP file
./rebuild_board.py ./botcover_edge_cuts.json
