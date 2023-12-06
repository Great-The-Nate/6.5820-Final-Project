import imageio
import os
import numpy as np
import json
from PIL import Image
from PIL.Image import Image as ImageType
from skimage.metrics import structural_similarity as ssim
import cv2


ROOT_INPUT_DIR = os.path.join("real", "data", "tmp")
INPUT_VIDEO = os.path.join("real", "data", "clutch-livestream-moment.mp4")
SAMPLE_FREQ = 10  # Save every Nth frame
ORIGINAL_CLIPS_PATH = os.path.join(ROOT_INPUT_DIR, "original")
ORIGINAL_FRAMES_PATH = os.path.join(ORIGINAL_CLIPS_PATH, "frames")
os.makedirs(ORIGINAL_FRAMES_PATH, exist_ok=True)


# Get the original frames to compare against
def save_original_frames():
    for node in os.listdir(ORIGINAL_CLIPS_PATH):
        video_clip_file = os.path.join(ORIGINAL_CLIPS_PATH, node)
        if not os.path.isfile(video_clip_file):
            continue

        chunk_no = node.replace(".mp4", "").split("_")[1]
        video_reader = imageio.get_reader(video_clip_file, "ffmpeg")
        total_frames = 0
        for frame_number, image in enumerate(video_reader):
            total_frames += 1

            # Only get sample frequency frames to avoid making too many files
            if frame_number % SAMPLE_FREQ == 0:
                filepath = os.path.join(
                    ORIGINAL_FRAMES_PATH, f"original-{chunk_no}-{frame_number}.jpg"
                )
                if os.path.exists(filepath):
                    continue
                imageio.imwrite(filepath, image)


def load_original_frames() -> dict[int, dict[int, ImageType]]:
    original_frames = {}
    for node in os.listdir(ORIGINAL_FRAMES_PATH):
        path = os.path.join(ORIGINAL_FRAMES_PATH, node)

        chunk_no, frame_no = (
            node.replace(".jpg", "").replace("original-", "").split("-")
        )
        chunk_no, frame_no = int(chunk_no), int(frame_no)
        if chunk_no not in original_frames:
            original_frames[chunk_no] = {}
        original_frames[chunk_no][frame_no] = Image.open(path)

    return original_frames

save_original_frames()

original_frames = load_original_frames()
print(
    f"Loaded {len(original_frames)} chunks of original frames in memory ({original_frames.__sizeof__()} bytes)"
)

raw_ssim_scores = {}
for node in os.listdir(ROOT_INPUT_DIR):
    bitrate = node.split("-")[1]
    raw_ssim_scores[bitrate] = {}
    bitrate_dir = os.path.join(ROOT_INPUT_DIR, node)
    print(f"Getting average SSIM of the video with bitrate {bitrate}...")
    # Iterate through chunk clips
    for subnode in os.listdir(bitrate_dir):
        if not subnode.endswith(".mp4") or subnode.startswith("encoded"):
            continue

        # Get the chunk number and full file path
        chunk_no = int(subnode.replace(".mp4", "").split("_")[1])
        video_clip_file = os.path.join(bitrate_dir, subnode)
        raw_ssim_scores[bitrate][chunk_no] = {}

        video_reader = imageio.get_reader(video_clip_file, "ffmpeg")
        total_frames = 0
        for frame_no, image in enumerate(video_reader):
            total_frames += 1
            # Only get sample frequency frames to avoid making too many files
            if frame_no % SAMPLE_FREQ == 0:
                # Get the SSIM between the current image and the original image
                original_image = np.array(original_frames[chunk_no][frame_no])

                # print(image)
                original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
                compare_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                print(original_gray.shape)
                print(compare_gray.shape)
                score, diff = ssim(original_gray, compare_gray, full=True)

                print(f"{bitrate}\t{chunk_no}\t{frame_no}")
                raw_ssim_scores[bitrate][chunk_no][frame_no] = score

        print(f"\t> Read video file {subnode} ({chunk_no=}), had {total_frames} frames")

with open(os.path.join("real", "data", "raw-ssim-scores.json"), "w") as f:
    json.dump(raw_ssim_scores, f, indent=2)
# # Get raw video
# reader = imageio.get_reader(INPUT_VIDEO)

# for frame_number, image in enumerate(reader):
#     # im is numpy array
#     if frame_number % 10 == 0:
#         imageio.imwrite(f"frame_{frame_number}.jpg", image)
