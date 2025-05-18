import argparse
import json
import matplotlib.pyplot as plt
from satin_fill import generate_satin_fill

def load_contours(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

def generate_stitch_paths(contours_data, spacing=2.0, width=20):
    stitch_paths = []

    for entry in contours_data:
        color = tuple(entry["color"])
        for contour in entry["contours"]:
            if len(contour) < 4:
                continue  # skip invalid polygons
            try:
                fill_lines = generate_satin_fill(contour, spacing=spacing, width=width)
                for x0, y0, x1, y1 in fill_lines:
                    stitch_paths.append((color, [(x0, y0), (x1, y1)]))
            except Exception as e:
                print(f"Error processing contour {contour[:5]}...: {e}")

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

    plt.title("Satin Stitch Fill Paths")
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to contours JSON (from vectorize.py)")
    parser.add_argument("--spacing", type=float, default=2.0, help="Spacing between stitch lines (pixels)")
    parser.add_argument("--width", type=float, default=20.0, help="Half-width of satin fill sweep (pixels)")
    args = parser.parse_args()

    contour_data = load_contours(args.file)
    stitch_paths = generate_stitch_paths(contour_data, spacing=args.spacing, width=args.width)
    visualize_stitch_paths(stitch_paths)

if __name__ == "__main__":
    main()
