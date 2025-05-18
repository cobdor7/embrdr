import argparse
from pyembroidery import read, COLOR_CHANGE
import matplotlib.pyplot as plt

def plot_pes(file_path):
    pattern = read(file_path)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(f"PES Stitch Preview: {file_path}")
    ax.axis("equal")
    ax.axis("off")

    segments = []
    current_segment = []
    current_color_index = 0

    for stitch in pattern.stitches:
        if stitch[2] == COLOR_CHANGE:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
                current_color_index += 1
        else:
            current_segment.append((stitch[0], -stitch[1]))  # Flip Y

    if current_segment:
        segments.append(current_segment)

    thread_colors = pattern.threadlist
    for i, segment in enumerate(segments):
        x, y = zip(*segment)
        color = thread_colors[i % len(thread_colors)].hex_color()
        ax.plot(x, y, color=color, linewidth=1)

    plt.show()

def main():
    parser = argparse.ArgumentParser(description="View a .PES embroidery file with color changes.")
    parser.add_argument("file", help="Path to the .PES file")
    args = parser.parse_args()
    plot_pes(args.file)

if __name__ == "__main__":
    main()
