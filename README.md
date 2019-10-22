# teslacam
Tesla Camera

This is a very simple python 3 script to help me consolidate my Tesla's raw camera data into nicely formatted videos.  It tries to maintain the same resolution as the original with the same video quality.

This also makes use of my nvidia video card GPUs to accelerate encoding.

usage: teslacam.py [-h] [--codec CODEC] [--number_of_encoders NUMBER_OF_ENCODERS]
                   [--keep_temp_folder KEEP_TEMP_FOLDER]
                   ffmpeg_folder_path base_input_folder_path base_output_folder_path

positional arguments:
  ffmpeg_folder_path    full path to ffmpeg binary folder containing ffmpeg.exe and ffprobe.exe
  base_input_folder_path
                        full path to the video folder containing dated folders
  base_output_folder_path
                        full path of the output folder for merged files and intermediate folder

optional arguments:
  -h, --help            show this help message and exit
  --codec CODEC         codec to use for encoding
  --number_of_encoders NUMBER_OF_ENCODERS
                        number of encoders to use
  --keep_temp_folder KEEP_TEMP_FOLDER
                        keep temporary working folder after extraction
