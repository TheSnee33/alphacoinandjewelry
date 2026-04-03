"""
Higginson Jewelry & Antiques Coin — Fusion 360 Python Script
Coin: 4 inch diameter | 5mm thick | Reeded edge
Front: Crescent moon with diamond logo — raised relief
Back: FLAT (for gluing to the Alpha coin)

HOW TO RUN IN FUSION 360:
1. Open Fusion 360
2. Tools menu > Add-Ins > Scripts and Add-Ins
3. Click the green + next to "My Scripts"
4. Name it "HigginsonCoin" and click OK
5. Replace all code in the editor with this script
6. Click Run
7. Export as STL: File > Export > STL

Bradford Communications LLC | Alpha Coin & Jewelry Project
"""

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent

        # ── COIN SPECIFICATIONS ──────────────────────────────────────
        DIAMETER_INCHES = 4.0
        THICKNESS_MM = 5.0
        RELIEF_HEIGHT_MM = 0.6
        RIM_HEIGHT_MM = 0.8
        REED_COUNT = 180
        REED_DEPTH_MM = 0.3

        # Convert to cm
        DIAMETER_CM = DIAMETER_INCHES * 2.54
        RADIUS_CM = DIAMETER_CM / 2
        THICKNESS_CM = THICKNESS_MM / 10
        RELIEF_CM = RELIEF_HEIGHT_MM / 10
        RIM_CM = RIM_HEIGHT_MM / 10
        REED_DEPTH_CM = REED_DEPTH_MM / 10

        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        extrudes = rootComp.features.extrudeFeatures
        centerPt = adsk.core.Point3D.create(0, 0, 0)

        # ── STEP 1: COIN BODY ────────────────────────────────────────
        coinSketch = sketches.add(xyPlane)
        coinSketch.name = "CoinBody"
        coinSketch.sketchCurves.sketchCircles.addByCenterRadius(centerPt, RADIUS_CM)

        prof = coinSketch.profiles.item(0)
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(THICKNESS_CM))
        coinExtrude = extrudes.add(extInput)
        coinBody = coinExtrude.bodies.item(0)
        coinBody.name = "HigginsonCoin"

        # ── STEP 2: RAISED RIM (top face only) ──────────────────────
        offsetPlanes = rootComp.constructionPlanes
        planeInput = offsetPlanes.createInput()
        planeInput.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(THICKNESS_CM))
        topPlane = offsetPlanes.add(planeInput)
        topPlane.name = "TopFace"

        rimSketch = sketches.add(topPlane)
        rimSketch.name = "RaisedRim"
        circles = rimSketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(centerPt, RADIUS_CM)
        circles.addByCenterRadius(centerPt, RADIUS_CM - 0.15)

        rimProf = None
        for i in range(rimSketch.profiles.count):
            p = rimSketch.profiles.item(i)
            area = p.areaProperties().area
            if rimProf is None or area < rimProf.areaProperties().area:
                rimProf = p

        if rimProf:
            rimInput = extrudes.createInput(rimProf, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            rimInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(RIM_CM))
            extrudes.add(rimInput)

        # ── STEP 3: REEDED EDGE ──────────────────────────────────────
        edgeSketch = sketches.add(xyPlane)
        edgeSketch.name = "ReededEdge"
        lines = edgeSketch.sketchCurves.sketchLines

        for i in range(REED_COUNT):
            angle = (2 * math.pi * i) / REED_COUNT
            ox = RADIUS_CM * math.cos(angle)
            oy = RADIUS_CM * math.sin(angle)
            ix = (RADIUS_CM - REED_DEPTH_CM) * math.cos(angle)
            iy = (RADIUS_CM - REED_DEPTH_CM) * math.sin(angle)

            p1 = adsk.core.Point3D.create(ox, oy, 0)
            p2 = adsk.core.Point3D.create(ix, iy, 0)
            lines.addByTwoPoints(p1, p2)

            half_width = 0.012
            angle_offset = half_width / RADIUS_CM
            a1 = angle - angle_offset
            a2 = angle + angle_offset

            p3 = adsk.core.Point3D.create(RADIUS_CM * math.cos(a1), RADIUS_CM * math.sin(a1), 0)
            p4 = adsk.core.Point3D.create(RADIUS_CM * math.cos(a2), RADIUS_CM * math.sin(a2), 0)
            p5 = adsk.core.Point3D.create((RADIUS_CM - REED_DEPTH_CM) * math.cos(a1),
                                           (RADIUS_CM - REED_DEPTH_CM) * math.sin(a1), 0)
            p6 = adsk.core.Point3D.create((RADIUS_CM - REED_DEPTH_CM) * math.cos(a2),
                                           (RADIUS_CM - REED_DEPTH_CM) * math.sin(a2), 0)
            lines.addByTwoPoints(p3, p4)
            lines.addByTwoPoints(p5, p6)
            lines.addByTwoPoints(p3, p5)
            lines.addByTwoPoints(p4, p6)

        # ── STEP 4: HIGGINSON LOGO — CRESCENT MOON WITH DIAMOND ─────
        logoSketch = sketches.add(topPlane)
        logoSketch.name = "HigginsonLogo_Relief"
        arcs = logoSketch.sketchCurves.sketchArcs
        logoLines = logoSketch.sketchCurves.sketchLines
        logoCircles = logoSketch.sketchCurves.sketchCircles
        splines = logoSketch.sketchCurves.sketchFittedSplines

        # Logo positioned in upper portion of coin face
        # Scale: coin radius ~5.08cm, logo should fit in ~4cm area
        SC = 0.013  # scale from SVG-like coords to cm

        # --- Crescent Moon ---
        # Outer arc of crescent (large arc going over the top)
        moon_cx = 0
        moon_cy = 1.0  # offset upward from center

        # Outer boundary of crescent moon
        moon_r_outer = 140 * SC  # ~1.82cm
        moon_r_inner = 100 * SC  # ~1.30cm
        moon_inner_offset_y = 15 * SC  # inner circle shifted up slightly

        # Draw outer moon arc (nearly full circle, open at bottom)
        outer_pts = adsk.core.ObjectCollection.create()
        for i in range(49):
            t = math.pi * 0.15 + (math.pi * 1.7) * i / 48  # ~300 degree arc
            x = moon_cx + moon_r_outer * math.cos(t)
            y = moon_cy + moon_r_outer * math.sin(t)
            outer_pts.add(adsk.core.Point3D.create(x, y, 0))
        splines.add(outer_pts)

        # Draw inner moon arc (creates the crescent shape)
        inner_pts = adsk.core.ObjectCollection.create()
        for i in range(49):
            t = math.pi * 0.2 + (math.pi * 1.6) * i / 48
            x = moon_cx + moon_r_inner * math.cos(t)
            y = (moon_cy + moon_inner_offset_y) + (moon_r_inner * 1.15) * math.sin(t)
            inner_pts.add(adsk.core.Point3D.create(x, y, 0))
        splines.add(inner_pts)

        # Crescent tip connectors (close the shape)
        # Left tip
        left_outer_x = moon_cx + moon_r_outer * math.cos(math.pi * 0.15)
        left_outer_y = moon_cy + moon_r_outer * math.sin(math.pi * 0.15)
        left_inner_x = moon_cx + moon_r_inner * math.cos(math.pi * 0.2)
        left_inner_y = (moon_cy + moon_inner_offset_y) + (moon_r_inner * 1.15) * math.sin(math.pi * 0.2)
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(left_outer_x, left_outer_y, 0),
            adsk.core.Point3D.create(left_inner_x, left_inner_y, 0)
        )
        # Right tip
        right_outer_x = moon_cx + moon_r_outer * math.cos(math.pi * 1.85)
        right_outer_y = moon_cy + moon_r_outer * math.sin(math.pi * 1.85)
        right_inner_x = moon_cx + moon_r_inner * math.cos(math.pi * 1.8)
        right_inner_y = (moon_cy + moon_inner_offset_y) + (moon_r_inner * 1.15) * math.sin(math.pi * 1.8)
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(right_outer_x, right_outer_y, 0),
            adsk.core.Point3D.create(right_inner_x, right_inner_y, 0)
        )

        # --- Filigree scrollwork on crescent ---
        # Left scroll
        scroll_pts_l = adsk.core.ObjectCollection.create()
        scroll_l = [(-90, 40), (-70, 20), (-55, 35), (-40, 50), (-55, 65), (-70, 75), (-85, 60)]
        for sx, sy in scroll_l:
            scroll_pts_l.add(adsk.core.Point3D.create(sx * SC, moon_cy - sy * SC, 0))
        splines.add(scroll_pts_l)

        # Center scroll
        scroll_pts_c = adsk.core.ObjectCollection.create()
        scroll_c = [(-20, 55), (0, 35), (20, 55), (35, 70), (15, 80), (-15, 80), (-35, 70)]
        for sx, sy in scroll_c:
            scroll_pts_c.add(adsk.core.Point3D.create(sx * SC, moon_cy - sy * SC, 0))
        splines.add(scroll_pts_c)

        # Right scroll
        scroll_pts_r = adsk.core.ObjectCollection.create()
        scroll_r = [(55, 35), (70, 20), (90, 40), (100, 55), (85, 65), (70, 75), (55, 60)]
        for sx, sy in scroll_r:
            scroll_pts_r.add(adsk.core.Point3D.create(sx * SC, moon_cy - sy * SC, 0))
        splines.add(scroll_pts_r)

        # --- Pedestal/base column ---
        ped_w = 12 * SC
        ped_h = 30 * SC
        ped_y_bottom = moon_cy - 10 * SC
        p1 = adsk.core.Point3D.create(-ped_w, ped_y_bottom - ped_h, 0)
        p2 = adsk.core.Point3D.create(ped_w, ped_y_bottom - ped_h, 0)
        p3 = adsk.core.Point3D.create(ped_w, ped_y_bottom, 0)
        p4 = adsk.core.Point3D.create(-ped_w, ped_y_bottom, 0)
        logoLines.addByTwoPoints(p1, p2)
        logoLines.addByTwoPoints(p2, p3)
        logoLines.addByTwoPoints(p3, p4)
        logoLines.addByTwoPoints(p4, p1)

        # --- Diamond ring circle (center of crescent) ---
        ring_cy = moon_cy + 10 * SC
        logoCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, ring_cy, 0),
            28 * SC
        )

        # --- Diamond gem above ring ---
        d_cx = 0
        d_cy = moon_cy + 55 * SC
        d_hw = 22 * SC
        d_hh = 40 * SC

        dp1 = adsk.core.Point3D.create(d_cx, d_cy + d_hh, 0)       # top
        dp2 = adsk.core.Point3D.create(d_cx - d_hw, d_cy, 0)        # left
        dp3 = adsk.core.Point3D.create(d_cx, d_cy - d_hh, 0)        # bottom
        dp4 = adsk.core.Point3D.create(d_cx + d_hw, d_cy, 0)        # right
        logoLines.addByTwoPoints(dp1, dp2)
        logoLines.addByTwoPoints(dp2, dp3)
        logoLines.addByTwoPoints(dp3, dp4)
        logoLines.addByTwoPoints(dp4, dp1)
        # Facet lines
        logoLines.addByTwoPoints(dp1, dp3)
        logoLines.addByTwoPoints(dp2, dp4)

        # --- Sparkle lines above diamond ---
        spark_base = d_cy + d_hh
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(0, spark_base + 0.05, 0),
            adsk.core.Point3D.create(0, spark_base + 0.2, 0)
        )
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(-0.12, spark_base + 0.08, 0),
            adsk.core.Point3D.create(-0.2, spark_base + 0.15, 0)
        )
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(0.12, spark_base + 0.08, 0),
            adsk.core.Point3D.create(0.2, spark_base + 0.15, 0)
        )

        # --- Text guide arcs ---
        # "Higginson" text area (below the logo)
        textSketch = sketches.add(topPlane)
        textSketch.name = "TEXT_GUIDE_AddManually"

        # Arc for "Higginson" script text
        higg_pts = adsk.core.ObjectCollection.create()
        text_r_main = RADIUS_CM * 0.55
        for i in range(25):
            angle = -math.pi * 0.3 + (math.pi * 0.6) * i / 24
            x = text_r_main * math.cos(angle)
            y = -1.2 + text_r_main * math.sin(angle)
            higg_pts.add(adsk.core.Point3D.create(x, y, 0))
        textSketch.sketchCurves.sketchFittedSplines.add(higg_pts)

        # Arc for "Jewelry & Antiques" below
        ja_pts = adsk.core.ObjectCollection.create()
        text_r_sub = RADIUS_CM * 0.45
        for i in range(25):
            angle = -math.pi * 0.3 + (math.pi * 0.6) * i / 24
            x = text_r_sub * math.cos(angle)
            y = -2.0 + text_r_sub * math.sin(angle)
            ja_pts.add(adsk.core.Point3D.create(x, y, 0))
        textSketch.sketchCurves.sketchFittedSplines.add(ja_pts)

        # Top arc for "HIGGINSON JEWELRY & ANTIQUES"
        top_pts = adsk.core.ObjectCollection.create()
        text_r_top = RADIUS_CM * 0.85
        for i in range(25):
            angle = math.pi * 0.2 + (math.pi * 0.6) * i / 24
            x = text_r_top * math.cos(angle)
            y = text_r_top * math.sin(angle)
            top_pts.add(adsk.core.Point3D.create(x, y, 0))
        textSketch.sketchCurves.sketchFittedSplines.add(top_pts)

        # ── STEP 5: ATTEMPT TO EXTRUDE LOGO AS RELIEF ────────────────
        try:
            if logoSketch.profiles.count > 0:
                profilesToExtrude = adsk.core.ObjectCollection.create()
                for i in range(logoSketch.profiles.count):
                    profilesToExtrude.add(logoSketch.profiles.item(i))

                reliefInput = extrudes.createInput(
                    profilesToExtrude,
                    adsk.fusion.FeatureOperations.JoinFeatureOperation
                )
                reliefInput.setDistanceExtent(
                    False,
                    adsk.core.ValueInput.createByReal(RELIEF_CM)
                )
                extrudes.add(reliefInput)
        except:
            pass

        # ── SUCCESS ──────────────────────────────────────────────────
        ui.messageBox(
            "Higginson Logo Coin created!\n\n"
            "COIN SPECS:\n"
            f"  Diameter: {DIAMETER_INCHES}\" ({DIAMETER_CM*10:.1f}mm)\n"
            f"  Thickness: {THICKNESS_MM}mm\n"
            f"  Relief height: {RELIEF_HEIGHT_MM}mm\n"
            f"  Reeded edge: {REED_COUNT} grooves\n\n"
            "FRONT: Crescent moon + diamond logo in raised relief\n"
            "BACK: Flat (for gluing to Alpha coin)\n\n"
            "MANUAL STEPS:\n"
            "1. If logo relief didn't auto-extrude, select closed\n"
            "   profiles in 'HigginsonLogo_Relief' sketch and\n"
            "   extrude 0.6mm upward (Join)\n"
            "2. Add text 'Higginson' (script font) along the\n"
            "   first text guide arc\n"
            "3. Add 'Jewelry & Antiques' along second arc\n"
            "4. File > Export > STL\n\n"
            "Bradford Communications LLC"
        )

    except:
        if ui:
            ui.messageBox("Script Error:\n" + traceback.format_exc())
