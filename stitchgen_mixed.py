
import argparse
import json
import matplotlib.pyplot as plt
from satin_fill import generate_satin_fill

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

def load_contours(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

def generate_stitch_paths(contours_data, spacing=2.0, width=20, outline_step=2.0):
    stitch_paths = []

    for entry in contours_data:
        color = tuple(entry["color"])
        for contour in entry["contours"]:
            if len(contour) < 4:
                continue

            # Add fill
            try:
                fill_lines = generate_satin_fill(contour, spacing=spacing, width=width)
                for x0, y0, x1, y1 in fill_lines:
                    stitch_paths.append((color, [(x0, y0), (x1, y1)]))
            except Exception as e:
                print(f"Satin fill failed: {e} — fallback to running stitch")
                fallback = fallback_running_stitch(contour, step=spacing)
                for p0, p1 in fallback:
                    stitch_paths.append((color, [p0, p1]))

            # Add outline
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

    plt.title("Mixed Fill: Satin + Fallback Running Stitch")
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to contours JSON")
    parser.add_argument("--spacing", type=float, default=2.0)
    parser.add_argument("--width", type=float, default=20.0)
    args = parser.parse_args()

    contour_data = load_contours(args.file)
    stitch_paths = generate_stitch_paths(contour_data, spacing=args.spacing, width=args.width)
    visualize_stitch_paths(stitch_paths)

if __name__ == "__main__":
    main()
