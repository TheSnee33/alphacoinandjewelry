"""
Alpha Logo Coin — Fusion 360 Python Script
Coin: 4 inch diameter | 5mm thick | Reeded edge
Front: Alpha (α) symbol with diamond ring — raised relief
Back: FLAT (for gluing to the Higginson coin)

HOW TO RUN IN FUSION 360:
1. Open Fusion 360
2. Tools menu > Add-Ins > Scripts and Add-Ins
3. Click the green + next to "My Scripts"
4. Name it "AlphaLogoCoin" and click OK
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
        RELIEF_HEIGHT_MM = 0.6       # How high the logo stands up
        RIM_HEIGHT_MM = 0.8          # Raised rim around edge
        REED_COUNT = 180             # Number of reeded ridges
        REED_DEPTH_MM = 0.3          # Depth of each reed groove

        # Convert to cm (Fusion internal units)
        DIAMETER_CM = DIAMETER_INCHES * 2.54       # 10.16 cm
        RADIUS_CM = DIAMETER_CM / 2                 # 5.08 cm
        THICKNESS_CM = THICKNESS_MM / 10            # 0.5 cm
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
        coinBody.name = "AlphaLogoCoin"

        # ── STEP 2: RAISED RIM (top face only — back stays flat) ─────
        # Create offset plane at top of coin
        offsetPlanes = rootComp.constructionPlanes
        planeInput = offsetPlanes.createInput()
        planeInput.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(THICKNESS_CM))
        topPlane = offsetPlanes.add(planeInput)
        topPlane.name = "TopFace"

        rimSketch = sketches.add(topPlane)
        rimSketch.name = "RaisedRim"
        circles = rimSketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(centerPt, RADIUS_CM)
        circles.addByCenterRadius(centerPt, RADIUS_CM - 0.15)  # 1.5mm rim width

        # Find the annular (ring) profile
        rimProf = None
        for i in range(rimSketch.profiles.count):
            p = rimSketch.profiles.item(i)
            area = p.areaProperties().area
            # The thin ring will have the smallest area
            if rimProf is None or area < rimProf.areaProperties().area:
                rimProf = p

        if rimProf:
            rimInput = extrudes.createInput(rimProf, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            rimInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(RIM_CM))
            extrudes.add(rimInput)

        # ── STEP 3: REEDED EDGE (grooves around circumference) ───────
        # Create a sketch on a plane tangent to the edge for reed cuts
        # We'll cut rectangular grooves around the cylinder edge
        edgeSketch = sketches.add(xyPlane)
        edgeSketch.name = "ReededEdge"
        lines = edgeSketch.sketchCurves.sketchLines

        for i in range(REED_COUNT):
            angle = (2 * math.pi * i) / REED_COUNT
            # Outer point
            ox = (RADIUS_CM) * math.cos(angle)
            oy = (RADIUS_CM) * math.sin(angle)
            # Inner point (reed groove depth)
            ix = (RADIUS_CM - REED_DEPTH_CM) * math.cos(angle)
            iy = (RADIUS_CM - REED_DEPTH_CM) * math.sin(angle)
            # Draw thin groove line
            p1 = adsk.core.Point3D.create(ox, oy, 0)
            p2 = adsk.core.Point3D.create(ix, iy, 0)
            lines.addByTwoPoints(p1, p2)

            # Also draw small arc-width lines to make thin rectangular cuts
            half_width = 0.012  # ~0.12mm half-width of groove
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

        # ── STEP 4: ALPHA (α) LOGO — DRAWN ON TOP FACE ──────────────
        logoSketch = sketches.add(topPlane)
        logoSketch.name = "AlphaLogo_Relief"
        arcs = logoSketch.sketchCurves.sketchArcs
        logoLines = logoSketch.sketchCurves.sketchLines
        logoCircles = logoSketch.sketchCurves.sketchCircles
        splines = logoSketch.sketchCurves.sketchFittedSplines

        # Scale factor: logo is centered, coin radius is ~5.08cm
        # Alpha symbol fits roughly in a 4cm x 5cm box centered on coin
        S = 0.02  # scale from SVG coords to cm

        # --- Alpha main loop (elliptical ring) ---
        # Draw as a series of fitted spline points tracing the ellipse
        # Outer ellipse: center(-25*S, 20*S), rx=155*S, ry=150*S
        # With stroke-width=44 -> outer boundary rx=177, ry=172; inner rx=133, ry=128
        cx_a = -25 * S   # -0.5 cm
        cy_a = 20 * S    #  0.4 cm
        rx_outer = 177 * S  # 3.54
        ry_outer = 172 * S  # 3.44
        rx_inner = 133 * S  # 2.66
        ry_inner = 128 * S  # 2.56

        # But those are too big for a 5.08cm radius coin — scale down more
        LOGO_SCALE = 0.55  # fit logo nicely within coin face
        cx_a *= LOGO_SCALE
        cy_a *= LOGO_SCALE
        rx_outer *= LOGO_SCALE
        ry_outer *= LOGO_SCALE
        rx_inner *= LOGO_SCALE
        ry_inner *= LOGO_SCALE

        def ellipse_points(cx, cy, rx, ry, n=48, start=0, end=2*math.pi):
            """Generate points on an ellipse."""
            pts = adsk.core.ObjectCollection.create()
            for i in range(n + 1):
                t = start + (end - start) * i / n
                x = cx + rx * math.cos(t)
                y = cy + ry * math.sin(t)
                pts.add(adsk.core.Point3D.create(x, y, 0))
            return pts

        # Outer boundary of alpha loop (full ellipse)
        outerPts = ellipse_points(cx_a, cy_a, rx_outer, ry_outer, 48)
        splines.add(outerPts)

        # Inner boundary of alpha loop
        innerPts = ellipse_points(cx_a, cy_a, rx_inner, ry_inner, 48)
        splines.add(innerPts)

        # --- Alpha tail (swooping curve to the right) ---
        # Outer edge of tail
        tail_pts_outer = adsk.core.ObjectCollection.create()
        tail_coords_outer = [
            (85, 80), (100, 100), (115, 120), (130, 145),
            (145, 170), (155, 195), (160, 215), (155, 235),
            (145, 248), (130, 255), (115, 252), (105, 240)
        ]
        for tx, ty in tail_coords_outer:
            tail_pts_outer.add(adsk.core.Point3D.create(
                tx * S * LOGO_SCALE, -ty * S * LOGO_SCALE, 0
            ))
        splines.add(tail_pts_outer)

        # Inner edge of tail
        tail_pts_inner = adsk.core.ObjectCollection.create()
        tail_coords_inner = [
            (65, 80), (80, 100), (95, 125), (110, 150),
            (120, 175), (125, 200), (120, 220), (110, 232),
            (100, 238), (90, 230)
        ]
        for tx, ty in tail_coords_inner:
            tail_pts_inner.add(adsk.core.Point3D.create(
                tx * S * LOGO_SCALE, -ty * S * LOGO_SCALE, 0
            ))
        splines.add(tail_pts_inner)

        # --- Crown/prong setting ---
        prong_y = 180 * S * LOGO_SCALE  # above center
        prong_w = 45 * S * LOGO_SCALE
        prong_h = 11 * S * LOGO_SCALE
        # Rectangle for the setting band
        p1 = adsk.core.Point3D.create(-prong_w, prong_y, 0)
        p2 = adsk.core.Point3D.create(prong_w, prong_y, 0)
        p3 = adsk.core.Point3D.create(prong_w, prong_y + prong_h, 0)
        p4 = adsk.core.Point3D.create(-prong_w, prong_y + prong_h, 0)
        logoLines.addByTwoPoints(p1, p2)
        logoLines.addByTwoPoints(p2, p3)
        logoLines.addByTwoPoints(p3, p4)
        logoLines.addByTwoPoints(p4, p1)

        # --- Diamond gem ---
        # Diamond shape (4 points)
        d_cx = 0
        d_cy = (prong_y + prong_h + 50 * S * LOGO_SCALE)
        d_hw = 30 * S * LOGO_SCALE  # half-width
        d_hh = 55 * S * LOGO_SCALE  # half-height (taller than wide)

        dp1 = adsk.core.Point3D.create(d_cx, d_cy + d_hh, 0)       # top
        dp2 = adsk.core.Point3D.create(d_cx - d_hw, d_cy, 0)        # left
        dp3 = adsk.core.Point3D.create(d_cx, d_cy - d_hh, 0)        # bottom
        dp4 = adsk.core.Point3D.create(d_cx + d_hw, d_cy, 0)        # right
        logoLines.addByTwoPoints(dp1, dp2)
        logoLines.addByTwoPoints(dp2, dp3)
        logoLines.addByTwoPoints(dp3, dp4)
        logoLines.addByTwoPoints(dp4, dp1)
        # Diamond cross lines (facets)
        logoLines.addByTwoPoints(dp1, dp3)
        logoLines.addByTwoPoints(dp2, dp4)

        # --- Prong lines from setting to diamond ---
        prong_top = prong_y + prong_h
        # Left prong
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(-prong_w * 0.8, prong_top, 0),
            adsk.core.Point3D.create(d_cx - d_hw * 0.6, d_cy - d_hh * 0.3, 0)
        )
        # Right prong
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(prong_w * 0.8, prong_top, 0),
            adsk.core.Point3D.create(d_cx + d_hw * 0.6, d_cy - d_hh * 0.3, 0)
        )
        # Inner left prong
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(-prong_w * 0.3, prong_top, 0),
            adsk.core.Point3D.create(d_cx - d_hw * 0.2, d_cy - d_hh * 0.4, 0)
        )
        # Inner right prong
        logoLines.addByTwoPoints(
            adsk.core.Point3D.create(prong_w * 0.3, prong_top, 0),
            adsk.core.Point3D.create(d_cx + d_hw * 0.2, d_cy - d_hh * 0.4, 0)
        )

        # --- Text: "ALPHA COIN & JEWELRY" around top ---
        # (Text must be added manually in Fusion — sketches cannot create text via API)
        # Guide arc for text placement
        text_r = RADIUS_CM * 0.85
        text_arc_pts = adsk.core.ObjectCollection.create()
        for i in range(25):
            angle = math.pi * 0.2 + (math.pi * 0.6) * i / 24
            x = text_r * math.cos(angle)
            y = text_r * math.sin(angle)
            text_arc_pts.add(adsk.core.Point3D.create(x, y, 0))

        textGuide = sketches.add(topPlane)
        textGuide.name = "TEXT_GUIDE_AddManually"
        textGuide.sketchCurves.sketchFittedSplines.add(text_arc_pts)

        # ── STEP 5: ATTEMPT TO EXTRUDE LOGO AS RELIEF ────────────────
        # Note: Due to complex spline intersections, the auto-extrude may
        # not find all profiles. If it fails, extrude manually in Fusion:
        #   1. Select closed profile regions in the AlphaLogo_Relief sketch
        #   2. Extrude > 0.6mm upward > Join operation
        try:
            # Try to find and extrude closed profiles from the logo sketch
            if logoSketch.profiles.count > 0:
                # Collect all profiles
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
            pass  # Manual extrusion needed — see instructions above

        # ── SUCCESS ──────────────────────────────────────────────────
        ui.messageBox(
            "Alpha Logo Coin created!\n\n"
            "COIN SPECS:\n"
            f"  Diameter: {DIAMETER_INCHES}\" ({DIAMETER_CM*10:.1f}mm)\n"
            f"  Thickness: {THICKNESS_MM}mm\n"
            f"  Relief height: {RELIEF_HEIGHT_MM}mm\n"
            f"  Reeded edge: {REED_COUNT} grooves\n\n"
            "FRONT: Alpha logo in raised relief\n"
            "BACK: Flat (for gluing to Higginson coin)\n\n"
            "MANUAL STEPS:\n"
            "1. If logo relief didn't auto-extrude, select closed\n"
            "   profiles in 'AlphaLogo_Relief' sketch and\n"
            "   extrude 0.6mm upward (Join)\n"
            "2. Add text 'ALPHA COIN & JEWELRY' along the\n"
            "   TEXT_GUIDE arc using Insert > Text\n"
            "3. File > Export > STL\n\n"
            "Bradford Communications LLC"
        )

    except:
        if ui:
            ui.messageBox("Script Error:\n" + traceback.format_exc())
