import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from satin_fill import generate_satin_fill
from zigzag_fill import generate_zigzag_fill

def fallback_running_stitch(contour, step=2.0):
    simplified = []
    prev = contour[0]
    simplified.append(tuple(prev))
    dist_accum = 0.0

    for pt in contour[1:]:
        dx = pt[0] - prev[0]
        dy = pt[1] - prev[1]
        dist = (dx**2 + dy**2) ** 0.5
        dist_accum += dist

        if dist_accum >= step:
            simplified.append(tuple(pt))
            dist_accum = 0.0
            prev = pt

    if len(simplified) >= 2:
        return [(simplified[i], simplified[i + 1]) for i in range(len(simplified) - 1)]
    return []

def estimate_contour_angle(contour):
    data = np.array(contour)
    data = data - np.mean(data, axis=0)
    cov = np.cov(data.T)
    eigvals, eigvecs = np.linalg.eig(cov)
    major_axis = eigvecs[:, np.argmax(eigvals)]
    angle_rad = np.arctan2(major_axis[1], major_axis[0])
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def load_contours(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

def generate_stitch_paths(contours_data, spacing=2.0, width=None, outline_step=2.0,
                           use_satin=True, use_zigzag=True, use_outline=True):
    stitch_paths = []

    for entry in contours_data:
        color = tuple(entry["color"])
        for contour in entry["contours"]:
            if len(contour) < 4:
                continue

            # Add fill
            filled = False
            if use_satin:
                try:
                    angle = estimate_contour_angle(contour)
                    fill_lines = generate_satin_fill(contour, spacing=spacing, width=width, angle_deg=angle)
                    for x0, y0, x1, y1 in fill_lines:
                        stitch_paths.append((color, [(x0, y0), (x1, y1)]))
                    filled = True
                except Exception as e:
                    print(f"Satin fill failed: {e}")

            if not filled and use_zigzag:
                fallback = generate_zigzag_fill(contour, spacing=spacing)
                for x0, y0, x1, y1 in fallback:
                    stitch_paths.append((color, [(x0, y0), (x1, y1)]))
                filled = True

            if use_outline:
                outline = fallback_running_stitch(contour, step=outline_step)
                for p0, p1 in outline:
                    stitch_paths.append((color, [p0, p1]))

    return stitch_paths

def visualize_stitch_paths(stitch_paths, canvas_size=(128, 128)):
    plt.figure(figsize=(6, 6))
    plt.xlim(0, canvas_size[0])
    plt.ylim(canvas_size[1], 0)
    plt.axis("off")

    for color, path in stitch_paths:
        x, y = zip(*path)
        hex_color = "#{:02x}{:02x}{:02x}".format(*color)
        plt.plot(x, y, '-', color=hex_color, linewidth=1)

    plt.title("Dynamic Satin Angle Fill")
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to contours JSON")
    parser.add_argument("--spacing", type=float, default=2.0, help="Spacing between fill lines")
    parser.add_argument("--width", type=float, help="Half-width of satin sweep (auto if omitted)")
    parser.add_argument("--no-satin", action="store_true", help="Disable satin fill")
    parser.add_argument("--no-zigzag", action="store_true", help="Disable zig-zag fallback")
    parser.add_argument("--no-outline", action="store_true", help="Disable outline stitching")
    args = parser.parse_args()

    contour_data = load_contours(args.file)
    stitch_paths = generate_stitch_paths(
        contour_data,
        spacing=args.spacing,
        width=args.width,
        outline_step=args.spacing,
        use_satin=not args.no_satin,
        use_zigzag=not args.no_zigzag,
        use_outline=not args.no_outline
    )
    visualize_stitch_paths(stitch_paths)

if __name__ == "__main__":
    main()
