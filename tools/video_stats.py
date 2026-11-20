import argparse
import json
import math
import subprocess
from pathlib import Path

import cv2
import pandas as pd

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mpg", ".mpeg", ".mts", ".m2ts"}

def run_ffprobe(video_path: Path) -> dict:
    """
    Returns ffprobe JSON for the file (streams + format).
    Requires ffprobe in PATH.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return json.loads(out.decode("utf-8", errors="replace"))

def parse_fraction(frac: str) -> float:
    # ffprobe uses strings like "30000/1001"
    if not frac or frac == "0/0":
        return float("nan")
    num, den = frac.split("/")
    num = float(num)
    den = float(den)
    return num / den if den != 0 else float("nan")

def safe_float(x, default=float("nan")):
    try:
        return float(x)
    except Exception:
        return default

def extract_middle_frame_opencv(video_path: Path, out_path: Path, prefer_frame_index: int | None = None) -> bool:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return False

    # Try frame-index seek if we have it, else fall back to middle by duration.
    if prefer_frame_index is not None and prefer_frame_index >= 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, prefer_frame_index)
    else:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if frame_count > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
        else:
            # Fallback: seek by timestamp (ms)
            fps = cap.get(cv2.CAP_PROP_FPS) or 0
            if fps > 0:
                # try duration from cap properties if available
                # OpenCV often can’t give duration reliably; just read a frame after a rough seek
                cap.set(cv2.CAP_PROP_POS_MSEC, 0)

    ok, frame = cap.read()
    if not ok or frame is None:
        cap.release()
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ok2 = cv2.imwrite(str(out_path), frame)
    cap.release()
    return bool(ok2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=str, help="Folder containing videos")
    ap.add_argument("--out_csv", type=str, default="video_stats.csv", help="Output CSV path")
    ap.add_argument("--frames_dir", type=str, default=None, help="Optional: also save each video's middle frame here")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    frames_dir = Path(args.frames_dir).expanduser().resolve() if args.frames_dir else None
    out_csv = Path(args.out_csv).expanduser().resolve()

    videos = [p for p in folder.rglob("*") if p.suffix.lower() in VIDEO_EXTS]
    rows = []

    for vp in sorted(videos):
        row = {
            "file": vp.relative_to(Path.cwd()).as_posix() if vp.is_relative_to(Path.cwd()) else str(vp),
            "container_format": None,
            "size_bytes": vp.stat().st_size if vp.exists() else None,

            # video stream
            "v_codec": None,
            "width": None,
            "height": None,
            "pix_fmt": None,
            "bit_rate": None,
            "duration_s": None,
            "avg_fps": None,
            "r_fps": None,
            "nb_frames_reported": None,
            "frame_count_est": None,

            # audio stream (first)
            "a_codec": None,
            "a_channels": None,
            "a_sample_rate": None,
        }

        ff = None
        try:
            ff = run_ffprobe(vp)
        except Exception as e:
            row["error"] = f"ffprobe_failed: {e}"
            rows.append(row)
            continue

        fmt = ff.get("format", {}) or {}
        row["container_format"] = fmt.get("format_name")
        row["duration_s"] = safe_float(fmt.get("duration"))
        row["bit_rate"] = safe_float(fmt.get("bit_rate"))

        streams = ff.get("streams", []) or []
        vstreams = [s for s in streams if s.get("codec_type") == "video"]
        astreams = [s for s in streams if s.get("codec_type") == "audio"]

        if vstreams:
            vs = vstreams[0]
            row["v_codec"] = vs.get("codec_name")
            row["width"] = vs.get("width")
            row["height"] = vs.get("height")
            row["pix_fmt"] = vs.get("pix_fmt")

            avg_fps = parse_fraction(vs.get("avg_frame_rate", ""))
            r_fps = parse_fraction(vs.get("r_frame_rate", ""))

            row["avg_fps"] = avg_fps
            row["r_fps"] = r_fps

            nb_frames = vs.get("nb_frames")
            row["nb_frames_reported"] = int(nb_frames) if (nb_frames is not None and str(nb_frames).isdigit()) else None

            # Estimate frame count if nb_frames isn't reported (common for some containers/codecs)
            if row["nb_frames_reported"] is not None:
                row["frame_count_est"] = row["nb_frames_reported"]
            else:
                if row["duration_s"] and not math.isnan(avg_fps):
                    row["frame_count_est"] = int(round(row["duration_s"] * avg_fps))
                else:
                    row["frame_count_est"] = None

            # Extract middle frame image
            if frames_dir is not None:
                out_img = frames_dir / f"{vp.stem}_middle.jpg"
                prefer_idx = None
                if row["frame_count_est"] is not None:
                    prefer_idx = int(row["frame_count_est"] // 2)
                ok = extract_middle_frame_opencv(vp, out_img, prefer_frame_index=prefer_idx)
                row["middle_frame_path"] = str(out_img) if ok else None

        if astreams:
            a = astreams[0]
            row["a_codec"] = a.get("codec_name")
            row["a_channels"] = a.get("channels")
            row["a_sample_rate"] = a.get("sample_rate")

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)

    print(f"Found {len(videos)} videos under: {folder}")
    print(f"Wrote CSV: {out_csv}")
    if frames_dir:
        print(f"Middle frames saved to: {frames_dir}")

if __name__ == "__main__":
    main()