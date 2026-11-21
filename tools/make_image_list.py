import argparse
import csv
import os
import posixpath


def make_image_list(output, images_root="", release=None, airport=None,
                    viewpoint=None, surface=None, metadata_dir="metadata"):
    videos = {}
    manifest_path = os.path.join(metadata_dir, "manifest_v3.csv")
    with open(manifest_path, newline="", encoding="utf-8") as manifest:
        for row in csv.DictReader(manifest):
            if release and row["release"] != release:
                continue
            if airport and row["airport"] != airport:
                continue
            if viewpoint and row["viewpoint"] != viewpoint:
                continue
            videos[row["video_id"]] = row

    count = 0
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    samples_path = os.path.join(metadata_dir, "samples_v3.csv")
    with open(samples_path, newline="", encoding="utf-8") as samples, \
            open(output, "w", newline="", encoding="utf-8") as output_file:
        for row in csv.DictReader(samples):
            video_id = row["video_id"]
            if video_id not in videos:
                continue
            if surface and row["surface"] != surface:
                continue

            first = int(row["first_frame"])
            last = int(row["last_frame"])
            for frame_index in range(first, last + 1):
                filename = f"{video_id}-{frame_index:06d}.jpg"
                path = posixpath.join(images_root, filename) if images_root else filename
                output_file.write(path + "\n")
                count += 1
    return count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a line-oriented image manifest from AssistTaxi samples."
    )
    parser.add_argument("--output", default="metadata/image_list_v3.txt")
    parser.add_argument("--images-root", default="", help="Path prefix for extracted JPG files")
    parser.add_argument("--release", help="Restrict output to v1, v2, or v3")
    parser.add_argument("--airport", help="Restrict output to KMLB, X59, or X26")
    parser.add_argument("--viewpoint", help="Restrict output to a camera viewpoint")
    parser.add_argument("--surface", choices=("taxiway", "runway"),
                        help="Restrict output by surface")
    return parser.parse_args()


def main():
    args = parse_args()
    count = make_image_list(
        args.output,
        images_root=args.images_root,
        release=args.release,
        airport=args.airport,
        viewpoint=args.viewpoint,
        surface=args.surface,
    )
    print(f"Wrote {count} image paths to {args.output}")


if __name__ == "__main__":
    main()
