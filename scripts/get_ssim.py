import imageio
import os

ROOT_INPUT_DIR = os.path.join("real", "data", "tmp")
INPUT_VIDEO = os.path.join("real", "data", "clutch-livestream-moment.mp4")
OUTPUT_DIR = os.path.join("real", "data", "frames")
SAMPLE_FREQ = 10  # Save every Nth frame

os.makedirs(OUTPUT_DIR, exist_ok=True)

for node in os.listdir(ROOT_INPUT_DIR):
    bitrate = node.split("-")[1]
    bitrate_dir = os.path.join(ROOT_INPUT_DIR, node)
    print(f"Getting average SSIM of the video with bitrate {bitrate}...")
    # Iterate through chunk clips
    for subnode in os.listdir(bitrate_dir):
        if not subnode.endswith(".mp4") or subnode.startswith("encoded"):
            continue

        # Get the chunk number and full file path
        chunk_no = int(subnode.replace(".mp4", "").split("_")[1])
        video_clip_file = os.path.join(bitrate_dir, subnode)

        # video_reader = imageio.get_reader(video_clip_file, "ffmpeg")
        # total_frames = 0
        # for frame_number, image in enumerate(video_reader):
        #     total_frames += 1

        #     # Only get sample frequency frames to avoid making too many files
        #     if frame_number % SAMPLE_FREQ == 0:
        #         print(image)

        print(f"\t> Read video file {subnode} ({chunk_no=}), had {0} frames")

# # Get raw video
# reader = imageio.get_reader(INPUT_VIDEO)

# for frame_number, image in enumerate(reader):
#     # im is numpy array
#     if frame_number % 10 == 0:
#         imageio.imwrite(f"frame_{frame_number}.jpg", image)
