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
SAMPLE_FREQ = 50  # Save every Nth frame
ORIGINAL_CLIPS_PATH = os.path.join(ROOT_INPUT_DIR, "original")
ORIGINAL_FRAMES_PATH = os.path.join(ORIGINAL_CLIPS_PATH, "frames")
os.makedirs(ORIGINAL_FRAMES_PATH, exist_ok=True)


# Get the original frames to compare against
def save_original_frames():
    for node in os.listdir(ORIGINAL_CLIPS_PATH):
        print("Writing frames for clip", node)
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


# save_original_frames()

original_frames = load_original_frames()
print(
    f"Loaded {len(original_frames)} chunks of original frames in memory ({original_frames.__sizeof__()} bytes)"
)

raw_ssim_scores = {}
for node in sorted(os.listdir(ROOT_INPUT_DIR)):
    if node == "original":
        continue

    bitrate = node.split("-")[1]

    raw_ssim_scores[bitrate] = {}
    bitrate_dir = os.path.join(ROOT_INPUT_DIR, node)
    print(f"Getting average SSIM of the video with bitrate {bitrate}...")
    # Iterate through chunk clips
    for subnode in sorted(os.listdir(bitrate_dir)):
        if not subnode.endswith(".mp4") or subnode.startswith("encoded"):
            continue

        # Get the chunk number and full file path
        chunk_no = int(subnode.replace(".mp4", "").split("_")[1])
        video_clip_file = os.path.join(bitrate_dir, subnode)

        video_reader = imageio.get_reader(video_clip_file, "ffmpeg")
        total_frames = 0
        ssim_sum = 0
        for frame_no, image in enumerate(video_reader):
            # Only get sample frequency frames to avoid making too many files
            if frame_no % SAMPLE_FREQ == 0:
                # Get the SSIM between the current image and the original image
                try:
                    original_image = np.array(original_frames[chunk_no][frame_no])
                except KeyError:
                    print(
                        f"\t\t> Mismatch in number of frames, tried getting frame {frame_no} when original only has {len(original_frames[chunk_no])}"
                    )
                    continue

                # print(image)
                original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
                compare_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                score, diff = ssim(original_gray, compare_gray, full=True)
                ssim_sum += score
                total_frames += 1
                
        
        average_ssim = ssim_sum / total_frames
        raw_ssim_scores[bitrate][chunk_no] = average_ssim
        
        with open(os.path.join("real", "data", "raw-ssim-scores.json"), "w") as f:
            json.dump(raw_ssim_scores, f, indent=2)
            print("Successfully saved ssim scores to json")
        
        print(f"\t> Chunk {subnode} ({chunk_no=}), had {total_frames} valid frames and an average ssim of {average_ssim}")

