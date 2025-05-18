
import numpy as np
from shapely.geometry import Polygon, LineString
from skimage.draw import polygon2mask

def generate_zigzag_fill(contour, img_size=(128, 128), spacing=3.0, max_stitch_length=50):
    """
    Fills the interior of a contour using horizontal zig-zag lines.
    Returns a list of (x0, y0, x1, y1) stitch lines.
    """
    mask = polygon2mask(img_size, np.array(contour))
    poly = Polygon(contour)
    lines = []

    minx, miny, maxx, maxy = poly.bounds
    miny = max(int(miny), 0)
    maxy = min(int(maxy), img_size[0])

    reverse = False
    for y in range(miny, maxy, int(spacing)):
        scan = LineString([(minx - 1, y), (maxx + 1, y)])
        clipped = scan.intersection(poly)

        if clipped.is_empty:
            continue

        segments = []
        if clipped.geom_type == "LineString":
            coords = list(clipped.coords)
            if len(coords) == 2:
                segments.append(coords)
        elif clipped.geom_type == "MultiLineString":
            for seg in clipped.geoms:
                coords = list(seg.coords)
                if len(coords) == 2:
                    segments.append(coords)

        if reverse:
            segments = [s[::-1] for s in segments]

        for seg in segments:
            x0, y0 = seg[0]
            x1, y1 = seg[1]
            dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            if dist <= max_stitch_length:
                lines.append((x0, y0, x1, y1))

        reverse = not reverse

    return lines
