
import argparse
import os
import json
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from preprocess import preprocess_image
from vectorize import image_to_contours
from stitchgen_mixed import generate_stitch_paths
from pyembroidery import EmbPattern, STITCH, COLOR_CHANGE, write_pes

def save_reduced_image(image, path):
    image.save(path)
    print(f"Saved reduced image to {path}")

def save_contours(contours_by_color, out_path):
    serializable = []
    for color, contours in contours_by_color:
        color_key = [int(c) for c in color]
        simplified = []
        for cnt in contours:
            cnt = cnt.squeeze()
            if len(cnt.shape) == 2:
                simplified.append(cnt.tolist())
        serializable.append({"color": color_key, "contours": simplified})
    with open(out_path, "w") as f:
        json.dump(serializable, f)
    print(f"Saved contours to {out_path}")

def build_pes_file(stitch_paths, out_path):
    pattern = EmbPattern()
    last_color = None

    for color, path in stitch_paths:
        if color != last_color:
            pattern.add_command(COLOR_CHANGE)
            last_color = color
        for x, y in path:
            pattern.add_stitch_absolute(STITCH, x, y)

    pattern.end()
    write_pes(pattern, out_path)
    print(f"Saved .pes file to {out_path}")

def show_pipeline_images(orig, reduced, img_np, contours_by_color, stitch_paths):
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))

    # 1. Original
    axs[0].imshow(orig)
    axs[0].set_title("Original Image")
    axs[0].axis("off")

    # 2. Reduced
    axs[1].imshow(reduced)
    axs[1].set_title("Reduced Colors")
    axs[1].axis("off")

    # 3. Vectorized
    axs[2].set_xlim(0, img_np.shape[1])
    axs[2].set_ylim(img_np.shape[0], 0)
    axs[2].axis("off")
    for color, contours in contours_by_color:
        for cnt in contours:
            cnt = cnt.squeeze()
            if len(cnt.shape) == 2:
                patch = MplPolygon(cnt, edgecolor='black', facecolor='none', linewidth=1)
                axs[2].add_patch(patch)
    axs[2].set_title("Contours Only")


    # 4. Stitches
    axs[3].set_xlim(0, img_np.shape[1])
    axs[3].set_ylim(img_np.shape[0], 0)
    axs[3].axis("off")
    for color, path in stitch_paths:
        x, y = zip(*path)
        axs[3].plot(x, y, '-', color=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}", linewidth=1)
    axs[3].set_title("Stitch Paths")

    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input PNG file")
    parser.add_argument("--colors", type=int, default=6, help="Number of colors to reduce to")
    parser.add_argument("--spacing", type=float, default=2.0, help="Spacing between fill lines")
    parser.add_argument("--width", type=float, help="Half-width of satin sweep (auto if omitted)")
    parser.add_argument("--no-satin", action="store_true", help="Disable satin fill")
    parser.add_argument("--no-zigzag", action="store_true", help="Disable zig-zag fallback")
    parser.add_argument("--no-outline", action="store_true", help="Disable outline stitching")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory for output files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Step 1: Preprocess
    orig_img, reduced_img, palette = preprocess_image(args.file, n_colors=args.colors)
    reduced_path = os.path.join(args.output_dir, "reduced.png")
    save_reduced_image(reduced_img, reduced_path)

    # Step 2: Vectorize
    img_np, contours_by_color = image_to_contours(reduced_path)
    contour_json_path = os.path.join(args.output_dir, "contours.json")
    save_contours(contours_by_color, contour_json_path)

    # Step 3: Stitch Generation
    with open(contour_json_path, "r") as f:
        contour_data = json.load(f)
    stitch_paths = generate_stitch_paths(
        contour_data,
        spacing=args.spacing,
        width=args.width,
        use_satin=not args.no_satin,
        use_zigzag=not args.no_zigzag,
        use_outline=not args.no_outline
    )

    # Step 4: Visualize full pipeline
    show_pipeline_images(orig_img, reduced_img, img_np, contours_by_color, stitch_paths)

    # Step 5: Export PES
    pes_path = os.path.join(args.output_dir, "output.pes")
    build_pes_file(stitch_paths, pes_path)

if __name__ == "__main__":
    main()
