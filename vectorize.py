import argparse
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import json

def image_to_contours(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((128, 128), Image.LANCZOS)
    img_np = np.array(img)

    contours_by_color = []

    unique_colors = np.unique(img_np.reshape(-1, 3), axis=0)

    for color in unique_colors:
        mask = np.all(img_np == color, axis=-1).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_by_color.append((tuple(color), contours))

    return img_np, contours_by_color

def plot_contours(img_np, contours_by_color):
    plt.figure(figsize=(6, 6))
    plt.imshow(img_np)
    for color, contours in contours_by_color:
        for cnt in contours:
            cnt = cnt.squeeze()
            if len(cnt.shape) == 2:
                plt.plot(cnt[:, 0], cnt[:, 1], linewidth=1)
    plt.axis("off")
    plt.title("Vectorized Contours")
    plt.show()

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to reduced-color image")
    parser.add_argument("--save", type=str, help="Path to save contours JSON")
    args = parser.parse_args()

    img_np, contours_by_color = image_to_contours(args.file)
    plot_contours(img_np, contours_by_color)

    if args.save:
        save_contours(contours_by_color, args.save)

if __name__ == "__main__":
    main()
