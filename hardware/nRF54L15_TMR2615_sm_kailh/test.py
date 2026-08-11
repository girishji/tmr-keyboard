from build123d import *

try:
    from ocp_vscode import show, show_viewer
except ImportError:
    from ocp_vscode import show
    def show_viewer(): pass 

show_viewer()

with BuildPart() as my_part:
    with BuildSketch() as profile:
        with BuildLine() as outline:
            # 1. Start with a line
            l1 = Line((0, 0), (0, 20))
            
            # 2. Start the Bezier at the end of the previous line
            # In build123d, 'l1 @ 1' is the end of l1 (0 is start, 1 is end)
            l2 = Bezier(l1 @ 1, (10, 30), (20, -10), (30, 10))
            
            # 3. Continue from the end of the Bezier
            l3 = Line(l2 @ 1, (30, 0))
            l4 = Line(l3 @ 1, (0, 0))
            
        make_face()
    extrude(amount=5)


with BuildSketch() as centered_sketch:
    dxf_obj = import_svg("/Users/gp/git/tmr-keyboard/hardware/nRF54L15_kailh/botcase/botcase-Edge_Cuts.svg")
    # Move the center of the bounding box to (0,0)
    #add(dxf_obj.move(Location(-dxf_obj.center())))


show(dxf_obj, names=["Extruded Bezier"])