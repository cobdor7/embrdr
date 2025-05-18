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

    # === Stats ===
    total_stitches = len(pattern.stitches)
    color_changes = sum(1 for s in pattern.stitches if s[2] == COLOR_CHANGE)
    jump_stitches = sum(1 for s in pattern.stitches if s[2] not in (0, COLOR_CHANGE))

    x_vals = [s[0] for s in pattern.stitches]
    y_vals = [s[1] for s in pattern.stitches]
    width = max(x_vals) - min(x_vals)
    height = max(y_vals) - min(y_vals)

    print("=== Stitch Stats ===")
    print(f"File: {file_path}")
    print(f"Total stitches   : {total_stitches}")
    print(f"Color changes    : {color_changes}")
    print(f"Jump/trim ops    : {jump_stitches}")
    print(f"Design dimensions: {width:.2f} x {height:.2f} units")



    plt.show()

def main():
    parser = argparse.ArgumentParser(description="View a .PES embroidery file with color changes.")
    parser.add_argument("file", help="Path to the .PES file")
    args = parser.parse_args()
    plot_pes(args.file)

if __name__ == "__main__":
    main()
