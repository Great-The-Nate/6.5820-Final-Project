#!/bin/bash

# input_file=real/data/big_buck_bunny_360p24.y4m
input_file=real/data/clutch-livestream-moment.mp4
output_file=real/data/videos/video.dat
tmp_dir=real/data/tmp
segment_time=4

mkdir "$tmp_dir"

bitrates=(44 212)

chunk_sizes_files=()

# Look at var stream map in ffmpeg

# Iterate through the array using indices and values
for index in "${!bitrates[@]}"; do
    bitrate="${bitrates[$index]}"
    echo "========Encoding at bitrate $bitrate=========="

    bitrate_tmp_dir="$tmp_dir/br-$bitrate"
    mkdir "$bitrate_tmp_dir"

    # ffmpeg -i "$input_file" -c:v libx264 -b:v ""$bitrate"k"  -reset_timestamps 1 -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment "$bitrate_tmp_dir/chunk_%03d.mp4"

    bitrate_output="$bitrate_tmp_dir/chunk_sizes_$bitrate.txt"
    echo "Saving chunks to file"
    for file in $bitrate_tmp_dir/chunk_*.mp4; do
        size=$(wc -c < "$file")
        echo "$size" >> $bitrate_output
    done

    chunk_sizes_files+=("$bitrate_output")

    echo "$chunk_sizes_files"
done

echo "Saved chunk sizes files $chunk_sizes_files to output"
paste -d '\t' "${chunk_sizes_files[@]}" > "$output_file"
