#!/bin/bash

experiment_log=$1
tmp_dir="real/data/tmp"
tmp_clips_file="${tmp_dir}/clips.txt"

chunk_index=0
while IFS= read -r line; do
    # Use awk to extract and print the last value in the space-separated row
    bitrate=$(echo "$line" | awk '{print $NF}')
    formatted_index=$(printf "%03d" "$chunk_index")
    clip_filepath="br-${bitrate}k/chunk_${formatted_index}.mp4"

    echo "file ${clip_filepath}" >> "${tmp_clips_file}"

    ((chunk_index++))
done < "$experiment_log"

# Create the actual replay video
ffmpeg -f concat -safe 0 -i "${tmp_clips_file}" -c copy replay.mp4

rm "${tmp_clips_file}"