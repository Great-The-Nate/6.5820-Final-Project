#!/bin/bash

# input_file=real/data/big_buck_bunny_360p24.y4m
input_file=real/data/clutch-livestream-moment.mp4
output_file=real/data/videos/video.dat
tmp_dir=real/data/tmp
segment_time=4

mkdir "$tmp_dir"

bitrates=(44 86)

chunk_sizes_files=("real/data/tmp/br-44/chunk_sizes_44.txt" "real/data/tmp/br-86/chunk_sizes_86.txt")

# Iterate through the array using indices and values
# for index in "${!bitrates[@]}"; do
#     bitrate="${bitrates[$index]}"
#     echo "Encoding at bitrate $bitrate..."

#     bitrate_tmp_dir="$tmp_dir/br-$bitrate"
#     mkdir "$bitrate_tmp_dir"

#     ffmpeg -i "$input_file" -c:v libx264 -b:v "$bitrate"k  -reset_timestamps 1 -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment "$bitrate_tmp_dir/chunk_%03d.mp4"

#     bitrate_output="$bitrate_tmp_dir/chunk_sizes_$bitrate.txt"
#     echo "Saving chunks to file"
#     for file in $bitrate_tmp_dir/chunk_*.mp4; do
#         size=$(wc -c < "$file")
#         echo "$size" >> $bitrate_output
#     done

#     chunk_sizes_files+=("$bitrate_output")

#     echo
# done

echo "Saved chunk sizes files $chunk_sizes_files to output"
paste -d '\t' "${chunk_sizes_files[@]}" > "$output_file"

# ffmpeg -i "$input_file" -loglevel debug -c:v libx264 -preset slow -c:a aac "$tmp_dir/compressed.y4m"
# ffmpeg -i "$input_file" -c:v libx264 -b:v 44k  -reset_timestamps 1 -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment -map 0 -dn -f nut "tmp" | grep -oP 'Ssize:\K\d+' > chunk_sizes.txt
# Running command
# ffmpeg -i "$input_file" -c:v libx264 -b:v 44k  -reset_timestamps 1 -sc_threshold 0 -g $segment_time -force_key_frames "expr:gte(t, n_forced * $segment_time)" -segment_time $segment_time -f segment "$tmp_dir/output_%03d.mp4"

# for file in $tmp_dir/output_*.mp4; do
#     echo "Saving chunk $file..."
#     size=$(wc -c < "$file")
#     echo "$size" >> chunk_sizes.txt
# done
