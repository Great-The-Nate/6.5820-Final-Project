#!/bin/bash


# This script encodes a video file (.mp4) into several bitrates.
# 
# Input: A single video file as input (.mp4)
# Output: The script has 1 primary output, a single `.dat` file that contains
#   the chunk sizes of the video encoded at a variety of bitrates.  


input_file=real/data/videos/livestream/clutch-livestream-moments.mp4
output_file=real/data/videos/livestream/video.dat
tmp_dir=real/data/tmp
segment_time=4

bitrates=("44k")
# bitrates=("44k" "86k" "125k" "173k" "212k" "249k" "315k" "369k" "497k" "564k" "764k" "985k" "1178k" "1439k" "2038k" "2353k" "2875k" "3529k" "3844k")

mkdir "$tmp_dir"

# -----------------------------------
# STEP 1 - Segment the original video
# -----------------------------------
#
# Split the original video into chunks so that we can use the SSIM metric to
# compare encoded frames to the original.
split_original_video () {
    echo "Splitting original video into segments..."
    original_segments_filepattern="${tmp_dir}/original/chunk_%03d.mp4"
    mkdir "${tmp_dir}/original/"
    ffmpeg -i "$input_file" -c:v libx264 -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment -reset_timestamps 1 "$original_segments_filepattern"
    echo "Finished splitting original video!"
}

# ---------------------------------------------------------
# STEP 2 - Get chunk sizes of the video at various bitrates 
# ---------------------------------------------------------
#
# For each of the bitrates, encode the video at that bitrate and
# split it up into segments, similar as in step 1. Afterwords, calculate the
# size of each segment/chunk and save it to a file.
get_chunk_sizes () {
    echo "Getting chunk sizes for each bitrate..."

    # Iterate through the array using indices and values
    for bitrate in "${bitrates[@]}"; do
        encoded_video="${tmp_dir}/br-${bitrate}/encoded_${bitrate}.mp4"
        segment_file="${tmp_dir}/br-${bitrate}/chunk_%03d.mp4"

        mkdir "${tmp_dir}/br-${bitrate}"


        if [ -e "$encoded_video" ]; then
            echo "Encoded file exists already. Skipping to split phase..."
        else
            echo "File does not exist. Encoding at bitrate ${bitrate}..."
            # Encode the video
            ffmpeg -i "$input_file" -c:v libx264 -b:v "$bitrate" "$encoded_video"
        fi

        # Split the encoded video into 4-second segments
        echo "${segment_time}"
        ffmpeg -i "$encoded_video" -c:v libx264 -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment -reset_timestamps 1 "$segment_file"

        segment_sizes_file="${tmp_dir}/br-${bitrate}/${bitrate}_segment_sizes.txt"
        rm $segment_sizes_file

        # Save the segment sizes into a text file
        for file in $tmp_dir/br-$bitrate/chunk_*.mp4; do
            size=$(ffprobe -v error -select_streams v:0 -show_entries format=size -of default=noprint_wrappers=1:nokey=1 "$file")
            echo "$size" >> $segment_sizes_file
        done
    done

    echo "Successfully retrieved chunk sizes for each bitrate."
}


# --------------------------------------------
# STEP 3 - Save chunk sizes into a single file 
# --------------------------------------------
#
# Take each of the segment sizes files from the previous step and combine them
# into a single file.
save_chunk_sizes () {
    echo "Combining chunk sizes into single file..."

    chunk_sizes_files=()

    for bitrate in "${bitrates[@]}"; do
        chunk_sizes_files+=("${tmp_dir}/br-${bitrate}/${bitrate}_segment_sizes.txt")
    done

    for element in "${chunk_sizes_files[@]}"; do
        echo "$element"
    done

    printf "size %s\nbitrates " "${segment_time}" > "$output_file"
    printf "%s\t" "${bitrates[@]}" >> "$output_file"
    printf "\n" >> "$output_file"
    paste -d '\t' "${chunk_sizes_files[@]}" >> "$output_file"

    echo "Successfully saved output to ${output_file}!"
}

# split_original_video
get_chunk_sizes
save_chunk_sizes