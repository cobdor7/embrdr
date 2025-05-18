from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import argparse
import os

def preprocess_image(path, output_size=(128, 128), n_colors=6):
    img = Image.open(path).convert("RGB")
    img = img.resize(output_size, Image.LANCZOS)

    data = np.array(img)
    pixels = data.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors, n_init="auto").fit(pixels)
    labels = kmeans.labels_
    palette = kmeans.cluster_centers_.astype(np.uint8)

    quantized = palette[labels].reshape(data.shape)
    reduced_img = Image.fromarray(quantized)

    return img, reduced_img, palette

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to image")
    parser.add_argument("--colors", type=int, default=6, help="Number of output colors")
    parser.add_argument("--save", type=str, help="Output path to save reduced image")
    args = parser.parse_args()

    original, reduced, palette = preprocess_image(args.file, n_colors=args.colors)

    if args.save:
        reduced.save(args.save)
        print(f"Saved reduced image to: {args.save}")

    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    ax[0].imshow(original)
    ax[0].set_title("Original")
    ax[0].axis("off")

    ax[1].imshow(reduced)
    ax[1].set_title(f"Reduced to {args.colors} Colors")
    ax[1].axis("off")

    plt.show()

if __name__ == "__main__":
    main()
