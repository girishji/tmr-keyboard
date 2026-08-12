# in laser cutting kerf is the thickness of the material the laser vaporizes. A
# laser beam usually has a width of about 0.1mm to 0.2mm. To make a part larger
# (so it fits tightly in a slot), you offset it outwards by half the kerf. To
# make a hole smaller, you offset it inwards.

from build123d import *
from ocp_vscode import show

kerf = 0.2
offset_amount = kerf / 2

with BuildSketch() as laser_part:
    # Create geometry with the Bezier
    with BuildLine() as outline:
        l1 = Line((0, 0), (0, 10))
        # Your Cubic Bezier (2 points, 2 control points)
        l2 = Bezier(l1.end, (5, 15), (15, 5), (20, 10))
        l3 = Line(l2.end, (20, 0))
        l4 = Line(l3.end, l1.start)
    make_face()

    # APPLY THE OFFSET
    # amount > 0 grows the part (External parts)
    # amount < 0 shrinks the part (Internal holes)
    offset(amount=offset_amount, kind=Kind.TANGENT)
    # kind=Kind.TANGENT ensures the offset follows the Bezier path smoothly.
    # Kind.ARC is also a good option if you want rounded corners on sharp
    # joints.

# Export the offset version for the laser
laser_part.sketch.export_dxf("precise_part.dxf")

show(laser_part)
