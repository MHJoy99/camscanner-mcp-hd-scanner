import os
import sys
import glob
import cv2
import numpy as np
from PIL import Image, JpegImagePlugin, PdfImagePlugin

def detect_and_crop(img):
    """
    Detect document bounds on contrasting background and crop/warp.
    """
    orig = img.copy()
    h, w = img.shape[:2]

    scale = 1000.0 / max(h, w)
    small = cv2.resize(img, (int(w * scale), int(h * scale)))
    sh, sw = small.shape[:2]

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    edges = cv2.Canny(blurred, 30, 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    paper_rect = None
    if contours:
        for c in contours[:3]:
            area = cv2.contourArea(c)
            if area > (sw * sh * 0.40):
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    paper_rect = approx.reshape(4, 2) / scale
                    break
                else:
                    x, y, bw, bh = cv2.boundingRect(c)
                    paper_rect = np.array([
                        [x, y], [x + bw, y], [x + bw, y + bh], [x, y + bh]
                    ], dtype=np.float32) / scale
                    break

    if paper_rect is not None:
        pts = np.zeros((4, 2), dtype="float32")
        s = paper_rect.sum(axis=1)
        pts[0] = paper_rect[np.argmin(s)]
        pts[2] = paper_rect[np.argmax(s)]
        diff = np.diff(paper_rect, axis=1)
        pts[1] = paper_rect[np.argmin(diff)]
        pts[3] = paper_rect[np.argmax(diff)]

        (tl, tr, br, bl) = pts
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        if maxWidth > 500 and maxHeight > 500:
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype="float32")

            M = cv2.getPerspectiveTransform(pts, dst)
            return cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

    margin_x = int(w * 0.025)
    margin_y = int(h * 0.025)
    return orig[margin_y:h-margin_y, margin_x:w-margin_x]

def enhance_magic_color(img):
    """
    CamScanner Magic Color:
    - Shadow removal & paper background whitening
    - Rich ink darkening & edge sharpening
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    dilated = cv2.dilate(gray, np.ones((11, 11), np.uint8))
    bg = cv2.medianBlur(dilated, 31)
    bg_32 = np.maximum(bg.astype(np.float32), 1.0)
    ratio = 255.0 / bg_32

    b, g, r = cv2.split(img.astype(np.float32))
    b = np.clip(b * ratio, 0, 255)
    g = np.clip(g * ratio, 0, 255)
    r = np.clip(r * ratio, 0, 255)
    color_normalized = cv2.merge([b, g, r]).astype(np.uint8)

    table = np.zeros(256, dtype=np.uint8)
    for i in range(256):
        if i >= 215:
            table[i] = 255
        elif i < 40:
            table[i] = int(i * 0.75)
        else:
            val = 30 + (i - 40) * (225.0 / (215 - 40))
            table[i] = np.clip(int(val), 0, 255)

    enhanced = cv2.LUT(color_normalized, table)

    kernel = np.array([
        [0, -0.3, 0],
        [-0.3, 2.2, -0.3],
        [0, -0.3, 0]
    ], dtype=np.float32)
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))

def convert_folder_to_hd_pdf(folder_path, output_pdf_path):
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.JPG", "*.JPEG", "*.PNG")
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(folder_path, ext)))
    
    files = sorted(list(set(files)))
    if not files:
        print(f"No images found in {folder_path}")
        return False

    print(f"Processing {len(files)} images from: {folder_path}")
    pages = []
    for idx, fpath in enumerate(files, 1):
        fname = os.path.basename(fpath)
        print(f"[{idx}/{len(files)}] Enhancing {fname}...")
        img = cv2.imread(fpath)
        if img is None:
            continue
        cropped = detect_and_crop(img)
        page = enhance_magic_color(cropped)
        pages.append(page)

    if pages:
        first = pages[0]
        rest = pages[1:]
        first.save(output_pdf_path, save_all=True, append_images=rest, quality=95, dpi=(300, 300))
        print(f"\n[SUCCESS] Saved HD Scanned PDF: {output_pdf_path}")
        print(f"Total pages: {len(pages)}")
        return True
    return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"D:\Camscanner PDF\PDF 1"
    out = sys.argv[2] if len(sys.argv) > 2 else r"D:\Camscanner PDF\output\Scanned_Document_HD.pdf"
    convert_folder_to_hd_pdf(target, out)
