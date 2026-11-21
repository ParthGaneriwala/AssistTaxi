import cv2
import heapq
import os

def variance_of_laplacian(image):
    """Compute the Laplacian variance to measure image sharpness."""
    return cv2.Laplacian(image, cv2.CV_64F).var()

def extract_top_sharpest_frames(video_path, output_dir, top_n=100):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    os.makedirs(output_dir, exist_ok=True)
    frame_heap = []  # Min-heap for top-N sharpest frames

    index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sharpness = variance_of_laplacian(gray)

        # Use heap to store (sharpness, frame index, frame)
        if len(frame_heap) < top_n:
            heapq.heappush(frame_heap, (sharpness, index, frame.copy()))
        else:
            heapq.heappushpop(frame_heap, (sharpness, index, frame.copy()))

        index += 1
        if index % 1000 == 0:
            print(f"Processed {index} frames...")

    # Sort frames by descending sharpness
    top_frames = sorted(frame_heap, reverse=True)

    for rank, (score, idx, frame) in enumerate(top_frames):
        filename = os.path.join(output_dir, f"top{rank+1:03d}_frame{idx:06d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename} (sharpness: {score:.2f})")

    cap.release()
    print("Finished extracting top sharpest frames!")

def extract_frames(video_path, output_dir, video_id, samples_csv=None):
    """Write frames as <video_id>-<frame index:06d>.jpg, the v3 sample IDs.
    With samples_csv (metadata/samples_v3.csv), only frames that are samples are written."""
    keep = None
    if samples_csv:
        import csv
        keep = [(int(r["first_frame"]), int(r["last_frame"]))
                for r in csv.DictReader(open(samples_csv, newline="")) if r["video_id"] == video_id]
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if keep is None or any(a <= index <= b for a, b in keep):
            cv2.imwrite(os.path.join(output_dir, f"{video_id}-{index:06d}.jpg"), frame)
        index += 1
    cap.release()
    print(f"Read {index} frames from {video_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Extract frames from an AssistTaxi video.")
    p.add_argument("video")
    p.add_argument("output_dir")
    p.add_argument("--video-id", help="write every frame as <video-id>-<index>.jpg (see metadata/manifest_v3.csv)")
    p.add_argument("--samples", help="with --video-id: only frames listed in this samples_v3.csv")
    p.add_argument("--top", type=int, default=100, help="otherwise: keep the N sharpest frames")
    a = p.parse_args()
    if a.video_id:
        extract_frames(a.video, a.output_dir, a.video_id, a.samples)
    else:
        extract_top_sharpest_frames(a.video, a.output_dir, a.top)
