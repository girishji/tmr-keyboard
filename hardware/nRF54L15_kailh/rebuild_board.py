#!/usr/bin/env python3

import sys
import json
from build123d import *
from math import atan2, degrees


def arc_from_3pts(p1, p2, p3):
    return ThreePointArc(
        Vector(*p1),
        Vector(*p2),
        Vector(*p3)
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: rebuild_board.py <edge_cuts.json>")
        sys.exit(1)

    json_path = sys.argv[1]

    with open(json_path) as f:
        shapes = json.load(f)

    with BuildSketch() as sketch:

        for s in shapes:

            if s["type"] == "line":
                Line(
                    Vector(*s["start"]),
                    Vector(*s["end"])
                )

            elif s["type"] == "arc":
                arc_from_3pts(
                    s["start"],
                    s["mid"],
                    s["end"]
                )

            elif s["type"] == "circle":
                Circle(
                    radius=s["radius"],
                    mode=Mode.ADD
                ).locate(Location(Vector(*s["center"])))

            elif s["type"] == "rectangle":
                x1, y1 = s["start"]
                x2, y2 = s["end"]
                Rectangle(
                    abs(x2 - x1),
                    abs(y2 - y1)
                ).locate(
                    Location(
                        Vector((x1 + x2)/2, (y1 + y2)/2)
                    )
                )

            elif s["type"] == "bezier":
                Bezier(
                    Vector(*s["p0"]),
                    Vector(*s["p1"]),
                    Vector(*s["p2"]),
                    Vector(*s["p3"])
                )

            elif s["type"] == "polygon":
                for outline in s["outlines"]:
                    pts = [Vector(*p) for p in outline]
                    Polygon(*pts)

    # Extrude board 1.6mm (standard PCB thickness)
    board = extrude(sketch.sketch, amount=1.6)

    show(board)


if __name__ == "__main__":
    main()
