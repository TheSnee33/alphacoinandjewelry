import numpy as np
from stl import mesh
import cv2
import os
from scipy.ndimage import zoom

def create_smooth_coin_stl(image_path, output_path, diameter_mm=76.2, base_thickness=2.0, max_relief=2.0, use_rembg=False, invert=False):
    print(f"Processing {image_path}...")
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return False
        
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error: Could not load {image_path}. Make sure it is a valid image.")
        return False

    alpha = None
    if use_rembg:
        try:
            import rembg
            from PIL import Image
            print("Running background removal...")
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            output_pil = rembg.remove(img_pil)
            img = cv2.cvtColor(np.array(output_pil), cv2.COLOR_RGBA2BGRA)
            print("Background removal complete.")
        except Exception as e:
            print(f"Background removal failed: {e}. Proceeding without it.")

    if len(img.shape) == 3 and img.shape[2] == 4:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        alpha = img[:, :, 3].astype(float) / 255.0
    elif len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if use_rembg:
            # Fallback simple white masking if rembg failed
            mask = cv2.inRange(gray, 240, 255)
            alpha = np.where(mask == 255, 0.0, 1.0)
    else:
        gray = img
        
    if alpha is None:
        alpha = np.ones_like(gray, dtype=float)

    if invert:
        gray = 255 - gray

    # Ensure background is zero height by applying alpha mask
    height_map = (gray.astype(float) / 255.0) * alpha

    # Generate cylindrical mesh nodes
    segments = 360 # smooth circle
    rings = 150    # concentric rings for top face resolution

    nodes = []
    
    # Bottom center is vertex 0
    nodes.append([0.0, 0.0, 0.0])
    
    # Top center is vertex 1
    img_h, img_w = height_map.shape
    center_y, center_x = img_h // 2, img_w // 2
    center_z = base_thickness + (height_map[center_y, center_x] * max_relief)
    nodes.append([0.0, 0.0, center_z])
    
    radius = diameter_mm / 2.0
    node_idx = 2
    
    # Evaluate height at continuous (x, y) coordinates mapped to image
    def get_height(x, y):
        nx = (x / diameter_mm) + 0.5
        ny = (y / diameter_mm) + 0.5
        px = int(nx * img_w)
        py = int(ny * img_h)
        px = max(0, min(img_w - 1, px))
        py = max(0, min(img_h - 1, img_h - 1 - py)) # flip Y
        return height_map[py, px] * max_relief

    # Generate bottom vertices
    bottom_ring_starts = []
    for r_idx in range(1, rings + 1):
        r = (r_idx / rings) * radius
        bottom_ring_starts.append(node_idx)
        for s in range(segments):
            angle = s * (2 * np.pi / segments)
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            nodes.append([x, y, 0.0])
            node_idx += 1
            
    # Generate top vertices
    top_ring_starts = []
    for r_idx in range(1, rings + 1):
        r = (r_idx / rings) * radius
        top_ring_starts.append(node_idx)
        for s in range(segments):
            angle = s * (2 * np.pi / segments)
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            z = base_thickness + get_height(x, y)
            nodes.append([x, y, z])
            node_idx += 1

    # Connect vertices into triangular faces
    faces = []
    
    # Bottom center -> ring 1
    r_start = bottom_ring_starts[0]
    for s in range(segments):
        n1 = r_start + s
        n2 = r_start + ((s + 1) % segments)
        faces.append([0, n2, n1]) 
        
    # Connect bottom rings
    for r_idx in range(rings - 1):
        r1 = bottom_ring_starts[r_idx]
        r2 = bottom_ring_starts[r_idx + 1]
        for s in range(segments):
            n1, n2 = r1 + s, r1 + ((s + 1) % segments)
            n3, n4 = r2 + s, r2 + ((s + 1) % segments)
            faces.append([n1, n2, n3])
            faces.append([n2, n4, n3])
            
    # Top center -> ring 1
    r_start = top_ring_starts[0]
    for s in range(segments):
        n1 = r_start + s
        n2 = r_start + ((s + 1) % segments)
        faces.append([1, n1, n2]) 
        
    # Connect top rings
    for r_idx in range(rings - 1):
        r1 = top_ring_starts[r_idx]
        r2 = top_ring_starts[r_idx + 1]
        for s in range(segments):
            n1, n2 = r1 + s, r1 + ((s + 1) % segments)
            n3, n4 = r2 + s, r2 + ((s + 1) % segments)
            faces.append([n1, n3, n2])
            faces.append([n2, n3, n4])

    # Connect walls (between outermost top and bottom rings)
    b_start = bottom_ring_starts[-1]
    t_start = top_ring_starts[-1]
    for s in range(segments):
        b1, b2 = b_start + s, b_start + ((s + 1) % segments)
        t1, t2 = t_start + s, t_start + ((s + 1) % segments)
        faces.append([b1, t1, b2])
        faces.append([b2, t1, t2])
        
    # Convert to numpy arrays
    nodes = np.array(nodes)
    faces = np.array(faces)
    
    # Create the final mesh and save
    print(f"Writing STL to {output_path} (Vertices: {len(nodes)}, Faces: {len(faces)})...")
    coin_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            coin_mesh.vectors[i][j] = nodes[f[j], :]
            
    coin_mesh.save(output_path)
    print(f"Successfully saved {output_path}!\n")
    return True

if __name__ == "__main__":
    # Generate the ring coin (using background removal to isolate the gold ring)
    create_smooth_coin_stl(
        "ring.png", 
        "alpha_ring_coin.stl", 
        diameter_mm=76.2, 
        base_thickness=2.0, 
        max_relief=2.0, 
        use_rembg=True,
        invert=False
    )
    
    # Generate the watch coin (background is already dark, text and watch are bright)
    create_smooth_coin_stl(
        "watch.png", 
        "higginson_watch_coin.stl", 
        diameter_mm=76.2, 
        base_thickness=2.0, 
        max_relief=2.0, 
        use_rembg=False,
        invert=False
    )
