"""
Higginson Jewelry & Antiques Coin — Fusion 360 Python Script (LIGHTWEIGHT)
Coin: 4 inch diameter | 5mm thick | Reeded edge
Front: Crescent moon with diamond logo — raised relief
Back: FLAT (for gluing to the Alpha coin)

HOW TO RUN:
1. UTILITIES > Scripts and Add-Ins
2. Select HigginsonCoin > Run
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
        DIAMETER_CM = 4.0 * 2.54
        RADIUS_CM = DIAMETER_CM / 2
        THICKNESS_CM = 0.5
        RIM_CM = 0.08
        REED_COUNT = 60
        REED_DEPTH_CM = 0.03

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
        coinExt.bodies.item(0).name = "HigginsonCoin"

        # ── TOP PLANE ────────────────────────────────────────────────
        planes = rootComp.constructionPlanes
        pInput = planes.createInput()
        pInput.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(THICKNESS_CM))
        topPlane = planes.add(pInput)
        topPlane.name = "TopFace"

        # ── RAISED RIM ───────────────────────────────────────────────
        sRim = sketches.add(topPlane)
        sRim.name = "Rim"
        sRim.sketchCurves.sketchCircles.addByCenterRadius(origin, RADIUS_CM)
        sRim.sketchCurves.sketchCircles.addByCenterRadius(origin, RADIUS_CM - 0.12)

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

        # ── REEDED EDGE ──────────────────────────────────────────────
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

        # ── HIGGINSON LOGO ON TOP FACE ───────────────────────────────
        sLogo = sketches.add(topPlane)
        sLogo.name = "HigginsonLogo_ExtrudeThis"
        splines = sLogo.sketchCurves.sketchFittedSplines
        logoLines = sLogo.sketchCurves.sketchLines
        logoCircles = sLogo.sketchCurves.sketchCircles

        # --- Crescent Moon ---
        # Outer arc (wide arc over the top, open at bottom)
        moon_r = 1.8   # cm
        moon_cy = 0.8   # shifted up

        outer_pts = adsk.core.ObjectCollection.create()
        for i in range(37):
            t = math.pi * 0.12 + (math.pi * 1.76) * i / 36
            x = moon_r * math.cos(t)
            y = moon_cy + moon_r * math.sin(t)
            outer_pts.add(adsk.core.Point3D.create(x, y, 0))
        splines.add(outer_pts)

        # Inner arc (creates crescent — shifted up and smaller)
        inner_r = 1.35
        inner_cy = moon_cy + 0.25

        inner_pts = adsk.core.ObjectCollection.create()
        for i in range(37):
            t = math.pi * 0.15 + (math.pi * 1.7) * i / 36
            x = inner_r * math.cos(t)
            y = inner_cy + (inner_r * 1.1) * math.sin(t)
            inner_pts.add(adsk.core.Point3D.create(x, y, 0))
        splines.add(inner_pts)

        # --- Diamond ring circle at center of crescent ---
        logoCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, moon_cy + 0.15, 0), 0.35
        )

        # --- Diamond gem above ring ---
        dcy = moon_cy + 0.85
        dhw = 0.3
        dhh = 0.45
        d1 = adsk.core.Point3D.create(0, dcy + dhh, 0)
        d2 = adsk.core.Point3D.create(-dhw, dcy, 0)
        d3 = adsk.core.Point3D.create(0, dcy - dhh, 0)
        d4 = adsk.core.Point3D.create(dhw, dcy, 0)
        logoLines.addByTwoPoints(d1, d2)
        logoLines.addByTwoPoints(d2, d3)
        logoLines.addByTwoPoints(d3, d4)
        logoLines.addByTwoPoints(d4, d1)

        # --- Pedestal/column below ring ---
        pw = 0.15
        ph = 0.4
        pby = moon_cy - 0.15
        logoLines.addByTwoPoints(adsk.core.Point3D.create(-pw, pby, 0), adsk.core.Point3D.create(pw, pby, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(pw, pby, 0), adsk.core.Point3D.create(pw, pby - ph, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(pw, pby - ph, 0), adsk.core.Point3D.create(-pw, pby - ph, 0))
        logoLines.addByTwoPoints(adsk.core.Point3D.create(-pw, pby - ph, 0), adsk.core.Point3D.create(-pw, pby, 0))

        # --- Simple filigree curves on crescent ---
        # Left scroll
        sl = adsk.core.ObjectCollection.create()
        for sx, sy in [(-1.1, 0.3), (-0.9, 0.1), (-0.7, 0.25), (-0.55, 0.45), (-0.7, 0.55)]:
            sl.add(adsk.core.Point3D.create(sx, moon_cy + sy, 0))
        splines.add(sl)

        # Center scroll
        sc = adsk.core.ObjectCollection.create()
        for sx, sy in [(-0.25, 0.0), (0, -0.15), (0.25, 0.0), (0.35, 0.15), (0, 0.2), (-0.35, 0.15)]:
            sc.add(adsk.core.Point3D.create(sx, moon_cy + sy - 0.35, 0))
        splines.add(sc)

        # Right scroll
        sr = adsk.core.ObjectCollection.create()
        for sx, sy in [(0.7, 0.25), (0.9, 0.1), (1.1, 0.3), (1.0, 0.5), (0.7, 0.55)]:
            sr.add(adsk.core.Point3D.create(sx, moon_cy + sy, 0))
        splines.add(sr)

        # --- Text guide line (for manually adding text) ---
        textGuide = adsk.core.ObjectCollection.create()
        tr = RADIUS_CM * 0.65
        for i in range(25):
            angle = -math.pi * 0.35 + (math.pi * 0.7) * i / 24
            textGuide.add(adsk.core.Point3D.create(tr * math.cos(angle), -1.5 + tr * math.sin(angle), 0))

        sText = sketches.add(topPlane)
        sText.name = "TEXT_GUIDE_Higginson"
        sText.sketchCurves.sketchFittedSplines.add(textGuide)

        # ── DONE ─────────────────────────────────────────────────────
        ui.messageBox(
            "Higginson Logo Coin created!\n\n"
            "Diameter: 4\" (101.6mm)\n"
            "Thickness: 5mm | Rim: 0.8mm\n"
            "Reeded edge: 60 reference lines\n\n"
            "NEXT STEPS:\n"
            "1. Select closed profiles in the\n"
            "   'HigginsonLogo_ExtrudeThis' sketch\n"
            "2. Extrude > 0.6mm upward > Join\n"
            "3. Add 'Higginson' text along guide arc\n"
            "4. Add 'Jewelry & Antiques' below\n"
            "5. File > Export > STL"
        )

    except:
        if ui:
            ui.messageBox("Error:\n" + traceback.format_exc())
