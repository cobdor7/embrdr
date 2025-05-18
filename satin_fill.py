import numpy as np
from shapely.geometry import Polygon, LineString
from skimage.draw import polygon2mask
from skimage.morphology import skeletonize

def generate_satin_fill(contour, img_size=(128, 128), spacing=2.0, width=20):
    """
    Generate satin stitch fill lines for a given closed contour.

    Parameters:
        contour: List of [x, y] points (must be closed shape)
        img_size: Size of the raster mask (H, W)
        spacing: Vertical step between skeleton points (in pixels)
        width: Max length of satin stitch arms (in pixels)

    Returns:
        List of (x0, y0, x1, y1) stitch lines
    """
    mask = polygon2mask(img_size, np.array(contour))
    skeleton = skeletonize(mask)
    coords = np.argwhere(skeleton)
    poly = Polygon(contour)

    satin_lines = []
    for y, x in coords[::int(spacing)]:
        normal = LineString([(x - width, y), (x + width, y)])
        clipped = normal.intersection(poly)

        if clipped.is_empty:
            continue
        if clipped.geom_type == 'LineString':
            satin_lines.append(clipped.coords[0] + clipped.coords[1])
        elif clipped.geom_type == 'MultiLineString':
            for seg in clipped.geoms:
                satin_lines.append(seg.coords[0] + seg.coords[1])

    return satin_lines
