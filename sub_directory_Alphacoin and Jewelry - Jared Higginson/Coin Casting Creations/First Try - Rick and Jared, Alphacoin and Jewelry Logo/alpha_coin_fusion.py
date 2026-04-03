"""
Alpha Coin & Jewelry — Custom Coin Generator
Fusion 360 Python Script
Coin: 2.5 inch diameter | 7mm thick | Cast Silver

HOW TO RUN THIS IN FUSION 360:
1. Open Fusion 360
2. Click Tools menu → Add-Ins → Scripts and Add-Ins
3. Click the green + button next to "My Scripts"
4. Name it "AlphaCoin" and click OK
5. Replace all code in the editor with this script
6. Click Run
7. The coin body will appear in your workspace

AFTER RUNNING:
- Front face sketch (for portrait relief) will be on the top face
- Back face sketch (for logo relief) will be on the bottom face
- Import the SVG files as sketches on each face to add the designs
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
        
        # Get the active design
        design = app.activeProduct
        rootComp = design.rootComponent
        
        # ── COIN SPECIFICATIONS ────────────────────────────────────────────────
        DIAMETER_INCHES = 2.5
        THICKNESS_MM = 7.0          # 7mm — good for casting
        EDGE_BEVEL_MM = 0.8         # Slight bevel on edge for realism
        RELIEF_DEPTH_MM = 0.4       # How deep the portrait/logo relief sinks
        
        # Convert to cm (Fusion uses cm internally)
        DIAMETER_CM = DIAMETER_INCHES * 2.54   # 6.35 cm
        RADIUS_CM = DIAMETER_CM / 2             # 3.175 cm
        THICKNESS_CM = THICKNESS_MM / 10        # 0.7 cm
        BEVEL_CM = EDGE_BEVEL_MM / 10
        RELIEF_CM = RELIEF_DEPTH_MM / 10
        
        # ── CREATE COIN BODY ───────────────────────────────────────────────────
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        
        # Create base circle sketch
        coinSketch = sketches.add(xyPlane)
        coinSketch.name = "CoinProfile"
        
        circles = coinSketch.sketchCurves.sketchCircles
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        coinCircle = circles.addByCenterRadius(centerPoint, RADIUS_CM)
        
        # Extrude coin body
        prof = coinSketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, 
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        distance = adsk.core.ValueInput.createByReal(THICKNESS_CM)
        extInput.setDistanceExtent(False, distance)
        coinBody = extrudes.add(extInput)
        
        # ── ADD EDGE BEVEL ─────────────────────────────────────────────────────
        # Get all edges of the coin for chamfering
        fillets = rootComp.features.chamferFeatures
        
        # Get the top and bottom circular edges
        topFace = None
        bottomFace = None
        
        for face in coinBody.bodies.item(0).faces:
            normal = face.evaluator.getNormalAtPoint(face.pointOnFace)[1]
            if normal.z > 0.9:
                topFace = face
            elif normal.z < -0.9:
                bottomFace = face
        
        # Collect edge edges for chamfer
        edgesForChamfer = adsk.core.ObjectCollection.create()
        for edge in coinBody.bodies.item(0).edges:
            edgesForChamfer.add(edge)
        
        chamferInput = fillets.createInput(
            edgesForChamfer,
            True
        )
        chamferInput.setToEqualDistance(
            adsk.core.ValueInput.createByReal(BEVEL_CM)
        )
        
        try:
            fillets.add(chamferInput)
        except:
            pass  # Chamfer optional — continues if it fails
        
        # ── FRONT FACE SKETCH (for portrait import) ────────────────────────────
        # Create offset plane for front face
        offsetPlanes = rootComp.constructionPlanes
        planeInput = offsetPlanes.createInput()
        
        offsetVal = adsk.core.ValueInput.createByReal(THICKNESS_CM)
        planeInput.setByOffset(xyPlane, offsetVal)
        frontPlane = offsetPlanes.add(planeInput)
        frontPlane.name = "FrontFace_ImportPortraitSVGHere"
        
        # Front face guide circle
        frontSketch = sketches.add(frontPlane)
        frontSketch.name = "FRONT_ImportPortraitSVG"
        
        frontCircles = frontSketch.sketchCurves.sketchCircles
        # Outer boundary
        frontCircles.addByCenterRadius(centerPoint, RADIUS_CM)
        # Inner area for portrait (slight inset from edge)
        frontCircles.addByCenterRadius(centerPoint, RADIUS_CM - 0.3)
        
        # ── BACK FACE SKETCH (for logo import) ────────────────────────────────
        backSketch = sketches.add(xyPlane)
        backSketch.name = "BACK_ImportLogoSVG"
        
        backCircles = backSketch.sketchCurves.sketchCircles
        backCircles.addByCenterRadius(centerPoint, RADIUS_CM)
        backCircles.addByCenterRadius(centerPoint, RADIUS_CM - 0.3)
        
        # ── ADD TEXT GUIDES ────────────────────────────────────────────────────
        # Front text: "ALPHA COIN & JEWELRY" arc around top
        # Back text: "alphacoinandjewelry.com" arc around bottom
        # (Text is added manually in Fusion after running script)
        
        # ── RENAME BODY ───────────────────────────────────────────────────────
        coinBody.bodies.item(0).name = "AlphaCoin_SilverBody"
        
        # ── SUCCESS MESSAGE ───────────────────────────────────────────────────
        ui.messageBox(
            "✅ Alpha Coin body created successfully!\n\n"
            "COIN SPECS:\n"
            f"• Diameter: {DIAMETER_INCHES}\" ({DIAMETER_CM*10:.1f}mm)\n"
            f"• Thickness: {THICKNESS_MM}mm\n"
            f"• Material: .999 Fine Silver (assign in Appearance)\n\n"
            "NEXT STEPS:\n"
            "1. Select the FRONT_ImportPortraitSVG sketch\n"
            "2. Insert > Insert SVG > choose alpha_coin_front.svg\n"
            "3. Scale to fit within inner circle\n"
            "4. Extrude/Emboss inward by 0.4mm\n\n"
            "5. Select the BACK_ImportLogoSVG sketch\n"
            "6. Insert > Insert SVG > choose alpha_coin_back.svg\n"
            "7. Scale to fit within inner circle\n"
            "8. Extrude/Emboss inward by 0.4mm\n\n"
            "9. File > Export > STL for 3D printing test mold\n\n"
            "Rick Bradford | Alpha Coin & Jewelry Project"
        )
        
    except:
        if ui:
            ui.messageBox(
                "Script Error:\n" + traceback.format_exc()
            )
