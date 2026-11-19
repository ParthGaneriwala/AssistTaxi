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

# Example usage
video_file = 'GX010009.mp4'
output_folder = 'output_frames'
extract_top_sharpest_frames(video_file, output_folder)
