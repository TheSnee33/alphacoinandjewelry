"""
Alpha Logo Coin — Fusion 360 Python Script (LIGHTWEIGHT)
Coin: 4 inch diameter | 5mm thick | Reeded edge
Front: Alpha (α) symbol with diamond ring — raised relief
Back: FLAT (for gluing to the Higginson coin)

HOW TO RUN:
1. UTILITIES > Scripts and Add-Ins
2. Select AlphaLogoCoin > Run
3. Then manually extrude the logo sketch profiles 0.6mm upward (Join)

Bradford Communications LLC | Alpha Coin & Jewelry Project
"""

import adsk.core
import adsk.fusion
import traceback
import math


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent

        # ── COIN SPECS ───────────────────────────────────────────────
        DIAMETER_CM = 4.0 * 2.54       # 4 inches = 10.16 cm
        RADIUS_CM = DIAMETER_CM / 2     # 5.08 cm
        THICKNESS_CM = 0.5              # 5mm
        RIM_CM = 0.08                   # 0.8mm raised rim
        REED_COUNT = 60                 # Fewer reeds to avoid crash
        REED_DEPTH_CM = 0.03            # 0.3mm

        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        extrudes = rootComp.features.extrudeFeatures
        origin = adsk.core.Point3D.create(0, 0, 0)

        # ── COIN BODY ────────────────────────────────────────────────
        s1 = sketches.add(xyPlane)
        s1.name = "CoinBody"
        s1.sketchCurves.sketchCircles.addByCenterRadius(origin, RADIUS_CM)

        ext1 = extrudes.createInput(
            s1.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext1.setDistanceExtent(False, adsk.core.ValueInput.createByReal(THICKNESS_CM))
        coinExt = extrudes.add(ext1)
        coinExt.bodies.item(0).name = "AlphaLogoCoin"

        # ── TOP PLANE ────────────────────────────────────────────────
        planes = rootComp.constructionPlanes
        pInput = planes.createInput()
        pInput.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(THICKNESS_CM))
        topPlane = planes.add(pInput)
        topPlane.name = "TopFace"

        # ── RAISED RIM (top face only) ───────────────────────────────
        sRim = sketches.add(topPlane)
        sRim.name = "Rim"
        sRim.sketchCurves.sketchCircles.addByCenterRadius(origin, RADIUS_CM)
        sRim.sketchCurves.sketchCircles.addByCenterRadius(origin, RADIUS_CM - 0.12)

        # Find the thin ring profile (smallest area)
        rimProf = None
        for i in range(sRim.profiles.count):
            p = sRim.profiles.item(i)
            a = p.areaProperties().area
            if rimProf is None or a < rimProf.areaProperties().area:
                rimProf = p

        if rimProf:
            rimExt = extrudes.createInput(rimProf, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            rimExt.setDistanceExtent(False, adsk.core.ValueInput.createByReal(RIM_CM))
            extrudes.add(rimExt)

        # ── REEDED EDGE (simple radial lines only) ───────────────────
        sReed = sketches.add(xyPlane)
        sReed.name = "ReededEdge_Reference"
        lines = sReed.sketchCurves.sketchLines
        for i in range(REED_COUNT):
            angle = (2 * math.pi * i) / REED_COUNT
            ox = RADIUS_CM * math.cos(angle)
            oy = RADIUS_CM * math.sin(angle)
            ix = (RADIUS_CM - REED_DEPTH_CM) * math.cos(angle)
            iy = (RADIUS_CM - REED_DEPTH_CM) * math.sin(angle)
            lines.addByTwoPoints(
                adsk.core.Point3D.create(ox, oy, 0),
                adsk.core.Point3D.create(ix, iy, 0)
            )

        # ── ALPHA LOGO ON TOP FACE ───────────────────────────────────
        sLogo = sketches.add(topPlane)
        sLogo.name = "AlphaLogo_ExtrudeThis"
        splines = sLogo.sketchCurves.sketchFittedSplines
        logoLines = sLogo.sketchCurves.sketchLines

        # Scale: the logo fits within ~3.5cm of coin center
        # Alpha main loop — outer boundary
        def make_ellipse_pts(cx, cy, rx, ry, n=36):
            pts = adsk.core.ObjectCollection.create()
            for i in range(n):
                t = 2 * math.pi * i / n
                pts.add(adsk.core.Point3D.create(cx + rx * math.cos(t), cy + ry * math.sin(t), 0))
            return pts

        # Outer edge of alpha ring
        splines.add(make_ellipse_pts(-0.15, 0.1, 2.0, 1.9, 36))
        # Inner edge of alpha ring
        splines.add(make_ellipse_pts(-0.15, 0.1, 1.5, 1.4, 36))

        # Alpha tail — outer curve
        tail_out = adsk.core.ObjectCollection.create()
        for tx, ty in [(1.0, -0.7), (1.3, -1.1), (1.5, -1.5), (1.55, -1.9),
                        (1.45, -2.2), (1.25, -2.4), (1.05, -2.35)]:
            tail_out.add(adsk.core.Point3D.create(tx, ty, 0))
        splines.add(tail_out)

        # Alpha tail — inner curve
        tail_in = adsk.core.ObjectCollection.create()
        for tx, ty in [(0.65, -0.7), (0.9, -1.1), (1.1, -1.5), (1.15, -1.8),
                        (1.05, -2.05), (0.9, -2.15)]:
            tail_in.add(adsk.core.Point3D.create(tx, ty, 0))
        splines.add(tail_in)

        # Crown/setting band (rectangle)
        bw = 0.5   # half-width
        by = 2.0   # y position (above center)
        bh = 0.15
        logoLines.addByTwoPoints(adsk.core.Point3D.create(-bw, by, 0), adsk.core.Point3D.create(bw, by, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(bw, by, 0), adsk.core.Point3D.create(bw, by + bh, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(bw, by + bh, 0), adsk.core.Point3D.create(-bw, by + bh, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(-bw, by + bh, 0), adsk.core.Point3D.create(-bw, by, 0))

        # Diamond gem
        dcy = 2.7
        dhw = 0.4   # half-width
        dhh = 0.6   # half-height
        d1 = adsk.core.Point3D.create(0, dcy + dhh, 0)
        d2 = adsk.core.Point3D.create(-dhw, dcy, 0)
        d3 = adsk.core.Point3D.create(0, dcy - dhh, 0)
        d4 = adsk.core.Point3D.create(dhw, dcy, 0)
        logoLines.addByTwoPoints(d1, d2)
        logoLines.addByTwoPoints(d2, d3)
        logoLines.addByTwoPoints(d3, d4)
        logoLines.addByTwoPoints(d4, d1)

        # Prongs (setting to diamond)
        logoLines.addByTwoPoints(adsk.core.Point3D.create(-0.4, by + bh, 0), adsk.core.Point3D.create(-0.3, dcy - dhh * 0.5, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(0.4, by + bh, 0), adsk.core.Point3D.create(0.3, dcy - dhh * 0.5, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(-0.15, by + bh, 0), adsk.core.Point3D.create(-0.1, dcy - dhh * 0.4, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(0.15, by + bh, 0), adsk.core.Point3D.create(0.1, dcy - dhh * 0.4, 0))

        # ── DONE ─────────────────────────────────────────────────────
        ui.messageBox(
            "Alpha Logo Coin created!\n\n"
            "Diameter: 4\" (101.6mm)\n"
            "Thickness: 5mm | Rim: 0.8mm\n"
            "Reeded edge: 60 reference lines\n\n"
            "NEXT STEPS:\n"
            "1. Select closed profiles in the\n"
            "   'AlphaLogo_ExtrudeThis' sketch\n"
            "2. Extrude > 0.6mm upward > Join\n"
            "3. Add text around rim if desired\n"
            "4. File > Export > STL"
        )

    except:
        if ui:
            ui.messageBox("Error:\n" + traceback.format_exc())
