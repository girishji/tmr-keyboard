# Fusion 360 Python script
# Imports cubic Bezier control points exported from KiCad.
#
# CSV format: one cubic Bezier per line:
#   x0,y0,x1,y1,x2,y2,x3,y3
#
# KiCad board internal coordinates are nanometers.
# Fusion 360 API geometry uses centimeters, so:
#   cm = nm / 10,000,000
#
# Each CSV row is created as its own degree-3 control-point spline.
# The four imported control points are fixed by default. This preserves the
# exact imported Bezier geometry while allowing new lines to be constrained
# coincident to the spline endpoints to close profiles.

import adsk.core
import adsk.fusion
import traceback
import csv


KICAD_NM_TO_FUSION_CM = 1.0 / 10_000_000.0

# Change to True only if you specifically want KiCad Y mirrored in Fusion.
INVERT_Y = True

SKETCH_NAME = 'KiCad Bezier Import'

# Fix all four control points of every imported cubic Bezier. Fixed points keep
# their imported X/Y positions but remain usable as targets for constraints on
# geometry drawn later (for example, a line endpoint coincident with a spline
# endpoint).
FIX_CONTROL_POINTS = True


def nm_to_cm(value):
    return float(value) * KICAD_NM_TO_FUSION_CM


def make_point(x_nm, y_nm):
    x = nm_to_cm(x_nm)
    y = nm_to_cm(y_nm)
    if INVERT_Y:
        y = -y
    return adsk.core.Point3D.create(x, y, 0.0)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Open a Fusion Design before running this script.')
            return

        dlg = ui.createFileDialog()
        dlg.title = 'Select KiCad cubic Bezier CSV'
        dlg.filter = 'CSV files (*.csv);;All files (*.*)'

        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return

        csv_path = dlg.filename
        bezier_rows = []

        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)

            for line_num, row in enumerate(reader, start=1):
                if not row or all(not cell.strip() for cell in row):
                    continue

                if len(row) != 8:
                    raise ValueError(
                        f'Line {line_num}: expected 8 values '
                        f'(x0,y0,x1,y1,x2,y2,x3,y3), got {len(row)}.'
                    )

                try:
                    values = [float(cell.strip()) for cell in row]
                except ValueError:
                    raise ValueError(
                        f'Line {line_num}: all 8 fields must be numeric.'
                    )

                bezier_rows.append(values)

        if not bezier_rows:
            ui.messageBox('The selected CSV contains no Bezier rows.')
            return

        root = design.rootComponent
        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = SKETCH_NAME

        splines = sketch.sketchCurves.sketchControlPointSplines
        degree3 = adsk.fusion.SplineDegrees.SplineDegreeThree

        created = 0
        fixed_points = 0

        for values in bezier_rows:
            x0, y0, x1, y1, x2, y2, x3, y3 = values

            control_points = [
                sketch.sketchPoints.add(make_point(x0, y0)),
                sketch.sketchPoints.add(make_point(x1, y1)),
                sketch.sketchPoints.add(make_point(x2, y2)),
                sketch.sketchPoints.add(make_point(x3, y3)),
            ]

            # SketchControlPointSplines.add expects a normal Python list of
            # SketchPoint objects, not an ObjectCollection.
            spline = splines.add(control_points, degree3)

            if not spline:
                raise RuntimeError(
                    f'Fusion failed to create Bezier segment {created + 1}.'
                )

            if FIX_CONTROL_POINTS:
                # Use the spline-owned control points after creation. These are
                # the authoritative points that drive the control frame.
                spline.isControlFrameDisplayed = True
                for point in spline.controlPoints:
                    point.isFixed = True
                    fixed_points += 1

            created += 1

        constraint_note = (
            f' Fixed {fixed_points} control points at their imported coordinates.'
            if FIX_CONTROL_POINTS else
            ' Control points were left unconstrained.'
        )

        ui.messageBox(
            f'Imported {created} cubic Bezier segments into sketch '
            f'"{SKETCH_NAME}".{constraint_note}\n\n'
            'You can close profiles with sketch lines and apply Coincident '
            'constraints between each line endpoint and spline endpoint.'
        )

    except Exception:
        if ui:
            ui.messageBox(
                'Bezier import failed:\n\n' + traceback.format_exc()
            )
