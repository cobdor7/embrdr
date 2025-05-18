import numpy as np
from shapely.geometry import Polygon, LineString
from skimage.draw import polygon2mask
from skimage.morphology import skeletonize
import math

def rotate_normal(x, y, width, angle_deg):
    angle = math.radians(angle_deg)
    dx = math.cos(angle) * width
    dy = math.sin(angle) * width
    return LineString([(x - dx, y - dy), (x + dx, y + dy)])

def generate_satin_fill(contour, img_size=(128, 128), spacing=2.0, width=None, angle_deg=0):
    """
    Generate satin stitch fill lines for a given closed contour.

    Parameters:
        contour: List of [x, y] points (must be a closed shape)
        img_size: Size of the raster mask (H, W)
        spacing: Step between skeleton points (pixels)
        width: Optional manual override of half-width of sweep (if None, auto-estimated)
        angle_deg: Angle in degrees of fill direction (0 = horizontal)

    Returns:
        List of (x0, y0, x1, y1) stitch lines
    """
    mask = polygon2mask(img_size, np.array(contour))
    skeleton = skeletonize(mask)
    coords = np.argwhere(skeleton)
    poly = Polygon(contour)

    # Auto-calculate half-width if not provided
    if width is None:
        minx, miny, maxx, maxy = poly.bounds
        diagonal = math.sqrt((maxx - minx) ** 2 + (maxy - miny) ** 2)
        width = diagonal / 2  # half of shape diagonal

    satin_lines = []
    for y, x in coords[::int(spacing)]:
        normal = rotate_normal(x, y, width, angle_deg)
        clipped = normal.intersection(poly)

        if clipped.is_empty:
            continue
        if clipped.geom_type == 'LineString':
            satin_lines.append(clipped.coords[0] + clipped.coords[1])
        elif clipped.geom_type == 'MultiLineString':
            for seg in clipped.geoms:
                satin_lines.append(seg.coords[0] + seg.coords[1])

    return satin_lines
