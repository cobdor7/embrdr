import numpy as np
from shapely.geometry import Polygon, LineString
from skimage.draw import polygon2mask

def generate_zigzag_fill(contour, img_size=(128, 128), spacing=3.0):
    """
    Fills the interior of a contour using horizontal zig-zag lines.
    Returns a list of (x0, y0, x1, y1) stitch lines.
    """
    mask = polygon2mask(img_size, np.array(contour))
    poly = Polygon(contour)
    lines = []

    for y in range(0, img_size[0], int(spacing)):
        scan = LineString([(0, y), (img_size[1], y)])
        clipped = scan.intersection(poly)

        if clipped.is_empty:
            continue
        if clipped.geom_type == "LineString":
            coords = list(clipped.coords)
            if len(coords) == 2:
                lines.append(coords[0] + coords[1])
        elif clipped.geom_type == "MultiLineString":
            for seg in clipped.geoms:
                coords = list(seg.coords)
                if len(coords) == 2:
                    lines.append(coords[0] + coords[1])

    return lines
