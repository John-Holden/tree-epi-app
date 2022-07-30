#!/bin/bash

# Animate all frames

frame_path=$1
anim_path=$2
name=$3

ffmpeg -y -r 10 -i ${frame_path}/img_%04d.png -c:v libx264  ${anim_path}/${name}.mp4
rm -rf ${frame_path}/img_*