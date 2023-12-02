#!/bin/bash

# input_file=real/data/big_buck_bunny_360p24.y4m
input_file=real/data/clutch-livestream-moment.mp4
output_file=real/data/videos/video.dat
tmp_dir=real/data/tmp
segment_time=4

mkdir "$tmp_dir"

bitrates=("44k" "86k" "125k" "173k" "212k" "564k" "985" "1178k" "1439k")

# Look at var stream map in ffmpeg

# Iterate through the array using indices and values
for bitrate in "${bitrates[@]}"; do
    output_file="${tmp_dir}/br-${bitrate}/encoded_${bitrate}.mp4"
    segment_file="${tmp_dir}/br-${bitrate}/chunk_%03d.mp4"

    mkdir "${tmp_dir}/br-${bitrate}"


    if [ -e "$output_file" ]; then
        echo "Encoded file exists already. Skipping to split phase..."
    else
        echo "File does not exist. Encoding..."
        # Encode the video
        ffmpeg -i "$input_file" -c:v libx264 -b:v "$bitrate" "$output_file"
    fi

    # Split the encoded video into 4-second segments
    ffmpeg -i "$output_file" -c copy -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment -reset_timestamps 1 "$segment_file"

    segment_sizes_file="${tmp_dir}/br-${bitrate}/${bitrate}_segment_sizes.txt"
    rm $segment_sizes_file

     # Save the segment sizes into a text file
     for file in $tmp_dir/br-$bitrate/chunk_*.mp4; do
        size=$(ffprobe -v error -select_streams v:0 -show_entries format=size -of default=noprint_wrappers=1:nokey=1 "$file")
        echo "$size" >> $segment_sizes_file
    done
done

chunk_sizes_files=()

for bitrate in "${bitrates[@]}"; do
    chunk_sizes_files+=("${tmp_dir}/br-${bitrate}/${bitrate}_segment_sizes.txt")
done

for element in "${chunk_sizes_files[@]}"; do
    echo "$element"
done

paste -d '\t' "${chunk_sizes_files[@]}" > real/data/videos/video.dat
