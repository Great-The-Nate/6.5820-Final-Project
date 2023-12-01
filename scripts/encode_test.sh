#!/bin/bash

input_file=real/data/big_buck_bunny_360p24.y4m
output_dir=real/data/videos/
tmp_dir=real/data/tmp

ffmpeg -i "$input_file" -loglevel debug -c:v copy -preset slow -c:a aac "$tmp_dir/compressed.y4m"

for file in $tmp_dir/output_*.y4m; do
    echo "Saving chunk $file..."
    size=$(ffprobe -i "$file" -show_entries frame=pkt_size -v quiet -of csv="p=0")
    echo "$size" >chunk_sizes.txt
done
