import argparse
import csv
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a line-oriented image manifest from AssistTaxi samples."
    )
    parser.add_argument("--output", default="metadata/image_list_v3.txt")
    parser.add_argument("--images-root", default="", help="Path prefix for extracted JPG files")
    parser.add_argument("--release", help="Restrict output to v1, v2, or v3")
    parser.add_argument("--airport", help="Restrict output to a KMLB, X59, or X26 airport")
    parser.add_argument("--viewpoint", help="Restrict output to a camera viewpoint")
    parser.add_argument("--surface", choices=("taxiway", "runway"), help="Restrict output by surface")
    return parser.parse_args()


def main():
    args = parse_args()

    videos = {}
    with open("metadata/manifest_v3.csv", newline="", encoding="utf-8") as manifest:
        for row in csv.DictReader(manifest):
            if args.release and row["release"] != args.release:
                continue
            if args.airport and row["airport"] != args.airport:
                continue
            if args.viewpoint and row["viewpoint"] != args.viewpoint:
                continue
            videos[row["video_id"]] = row

    count = 0
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open("metadata/samples_v3.csv", newline="", encoding="utf-8") as samples, \
            open(args.output, "w", newline="", encoding="utf-8") as output:
        for row in csv.DictReader(samples):
            video_id = row["video_id"]
            if video_id not in videos:
                continue
            if args.surface and row["surface"] != args.surface:
                continue

            first = int(row["first_frame"])
            last = int(row["last_frame"])
            for frame_index in range(first, last + 1):
                filename = f"{video_id}-{frame_index:06d}.jpg"
                path = os.path.join(args.images_root, filename) if args.images_root else filename
                output.write(path + "\n")
                count += 1

    print(f"Wrote {count} image paths to {args.output}")


if __name__ == "__main__":
    main()
