# teslacam
Tesla Camera

This is a very simple python 3 script to help me consolidate my Tesla's raw camera data into nicely formatted videos.  It tries to maintain the same resolution as the original with the same video quality by default.

This also makes use of nvidia video card GPUs to accelerate encoding.

```
usage: teslacam [-h] [--codec {hevc_nvenc,libx265}] [--preset PRESET] [--reduce REDUCE] [--layout {pyramid,tall_diamond,short_diamond,cross}] [--keep_temp_folder KEEP_TEMP_FOLDER]
                ffprobe_file_path ffmpeg_file_path input_folder_path output_folder_path

positional arguments:
  ffprobe_file_path     full path to ffprobe binary
  ffmpeg_file_path      full path to ffmpeg binary
  input_folder_path     full path to the video folder containing timestamped folders
  output_folder_path    full path of the output folder for merged files and temporary work folder

optional arguments:
  -h, --help            show this help message and exit
  --codec {hevc_nvenc,libx265}
                        codec to use for encoding
  --preset PRESET       preset to use for encoding
  --reduce REDUCE       percent to reduce video to
  --layout {pyramid,tall_diamond,short_diamond,cross}
                        camera layout
  --keep_temp_folder KEEP_TEMP_FOLDER
                        keep temporary working folder after extraction
```
FFMpeg download:
https://ffmpeg.org/download.html
