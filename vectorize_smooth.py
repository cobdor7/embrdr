
import cv2
import numpy as np
from PIL import Image

def image_to_contours(image_path, blur_ksize=3, canny_thresh1=50, canny_thresh2=150, min_points=10):
    image = Image.open(image_path).convert("RGB")
    img_np = np.array(image)
    h, w, _ = img_np.shape
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # Apply Gaussian blur to reduce pixelation edges
    blurred = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)

    # Canny edge detection
    edges = cv2.Canny(blurred, canny_thresh1, canny_thresh2)

    # Find contours
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    contours_by_color = []
    simplified = []
    for cnt in cnts:
        if len(cnt) >= min_points:
            # Check if contour is closed
            if not np.allclose(cnt[0], cnt[-1], atol=2):
                continue
            simplified.append(cnt)
    if simplified:
        contours_by_color.append(((0, 0, 0), simplified))

    return img_np, contours_by_color
