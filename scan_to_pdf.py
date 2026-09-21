import os
import glob
import cv2
import numpy as np
from PIL import Image

def process_image_to_scanned(image_path, enhance_mode="magic_color"):
    """
    Simulates CamScanner's 'Magic Color' filter:
    1. Removes shadows and uneven lighting via background normalization.
    2. Sharpens text details.
    3. Increases contrast while keeping colors vivid and paper background pure white.
    """
    img = cv2.imread(image_path)
    if img is None:
        # Fallback to PIL if cv2 can't read path (e.g. unicode characters)
        pil_temp = Image.open(image_path).convert('RGB')
        img = cv2.cvtColor(np.array(pil_temp), cv2.COLOR_RGB2BGR)

    # Convert to grayscale to compute lighting background
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Dilate + Median Blur to estimate background illumination
    dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
    bg = cv2.medianBlur(dilated, 21)

    # Difference image to eliminate shadows
    diff = 255 - cv2.absdiff(gray, bg)

    # Normalize difference
    norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

    if enhance_mode == "magic_color":
        # Magic Color: preserve original colors while brightening paper to white
        # Calculate scaling factor from grayscale normalization
        scale = norm.astype(np.float32) / (gray.astype(np.float32) + 1e-5)
        scale = np.clip(scale, 1.0, 3.0)
        
        b, g, r = cv2.split(img.astype(np.float32))
        b = np.clip(b * scale, 0, 255).astype(np.uint8)
        g = np.clip(g * scale, 0, 255).astype(np.uint8)
        r = np.clip(r * scale, 0, 255).astype(np.uint8)
        enhanced = cv2.merge([b, g, r])

        # Mild sharpening
        kernel = np.array([[0, -0.5, 0], [-0.5, 3.0, -0.5], [0, -0.5, 0]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        # Convert BGR to RGB for PIL
        enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
        return Image.fromarray(enhanced_rgb)

    elif enhance_mode == "bw":
        # Crisp B&W Document Filter
        bw = cv2.adaptiveThreshold(
            norm, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10
        )
        return Image.fromarray(bw).convert("L")
    
    else:
        # Grayscale clean
        return Image.fromarray(norm).convert("L")

def build_pdf(input_dir=".", output_pdf="scanned_document.pdf", enhance_mode="magic_color"):
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.JPG", "*.JPEG", "*.PNG")
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(input_dir, ext)))
    
    # Sort files naturally
    files = sorted(list(set(files)))
    
    if not files:
        print(f"No image files found in '{input_dir}'.")
        return False

    print(f"Found {len(files)} images to process...")
    processed_pages = []

    for idx, f in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] Processing {os.path.basename(f)} ({enhance_mode})...")
        try:
            page = process_image_to_scanned(f, enhance_mode=enhance_mode)
            # Ensure RGB
            if page.mode != "RGB":
                page = page.convert("RGB")
            processed_pages.append(page)
        except Exception as e:
            print(f"Error processing {f}: {e}")

    if processed_pages:
        out_path = os.path.join(input_dir, output_pdf)
        first_page = processed_pages[0]
        other_pages = processed_pages[1:] if len(processed_pages) > 1 else []
        first_page.save(out_path, save_all=True, append_images=other_pages, quality=95, dpi=(300, 300))
        print(f"\nSuccessfully generated: {out_path} ({len(processed_pages)} pages)")
        return True
    return False

if __name__ == "__main__":
    import sys
    mode = "magic_color"
    if len(sys.argv) > 1:
        mode = sys.argv[1] # magic_color or bw
    target_dir = os.path.dirname(os.path.abspath(__file__))
    build_pdf(input_dir=target_dir, output_pdf="Scanned_HD_Output.pdf", enhance_mode=mode)
