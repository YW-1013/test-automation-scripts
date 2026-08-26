import time
from moviepy import *
import os
import sys

current_working_dir = os.path.dirname(os.path.realpath(sys.argv[0])) # 当前工作目录

current_video = ["4K60.mp4","8K60.mkv"]
should_vide_4k = ["4K60.mov","4K60.avi","4K60.mkv"]
should_vide_8k = ["8K60.mov","8K60.avi","8K60.mp4"]
for i in should_vide_4k:
    input_filepath = os.path.join(current_working_dir, "4K60.mp4")
    
    # 确定输出文件路径
    output_filepath = os.path.join(current_working_dir, i)

    # 使用moviepy进行格式转换
    try:
        clip = VideoFileClip(input_filepath)
        clip.write_videofile(output_filepath, codec='libx264')
    except Exception as e:
        print(f"Failed to convert: {e}")
time.sleep(20)
for i in should_vide_8k:
    input_filepath = os.path.join(current_working_dir, "8K60.mkv")

    # 确定输出文件路径
    output_filepath = os.path.join(current_working_dir, i)

    # 使用moviepy进行格式转换
    try:
        clip = VideoFileClip(input_filepath)
        clip.write_videofile(output_filepath, codec='libx264')
    except Exception as e:
        print(f"Failed to convert: {e}")