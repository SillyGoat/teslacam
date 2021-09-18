# teslacam
Tesla Camera

This is a very simple python 3 script to help me consolidate my Tesla's raw camera data into nicely formatted videos.  It tries to maintain the same resolution as the original with the same video quality by default.

This also makes use of nvidia video card GPUs to accelerate encoding.

Installation:

Download FFMpeg here:
https://ffmpeg.org/download.html

Run:
```
python -m pip install teslacam
```
Command line usage
```
python -m teslacam --help
```
```
usage: teslacam [-h] [--codec {hevc_nvenc,libx265}] [--preset PRESET] [--reduce REDUCE] [--layout {pyramid,tall_diamond,short_diamond,cross}] [--keep_temp_folder KEEP_TEMP_FOLDER] [--log_level {debug,info,warning,error,critical,none}]
                ffprobe_file_path ffmpeg_file_path input_folder_path output_folder_path

positional arguments:
  ffprobe_file_path     Path to the ffprobe binary
  ffmpeg_file_path      Path to the ffmpeg binary
  input_folder_path     Path to the video folder containing timestamped folders
  output_folder_path    Path to the output folder containing both merged files and the temporary work folder

optional arguments:
  -h, --help            show this help message and exit
  --codec {hevc_nvenc,libx265}
                        Codec to use for encoding (default: hevc_nvenc)
  --preset PRESET       Codec's preset to use for encoding. See ffmpeg -h long for each codec's available presets (default: slow)
  --reduce REDUCE       Percent to reduce video to (default: 100)
  --layout {pyramid,tall_diamond,short_diamond,cross}
                        Camera layout (default: pyramid)
  --keep_temp_folder KEEP_TEMP_FOLDER
                        Keep temporary working folder after extraction (default: False)
  --log_level {debug,info,warning,error,critical,none}
                        Display log messages that matches or exceeds the severity of the specified level. Use "none" to disable messages (default: info)
```
API Usage
```
import teslacam
from teslacam import *

def main():
  print(f"Available layouts: {', '.join(teslacam.constants.LAYOUT.keys())}")
  print(f'Available codecs: {teslacam.constants.CODEC_OPTIONS.items()}')
  extract_videos(
    FFMpegPaths(
      r'some_ffmpeg_path\ffprobe.exe', # path to ffprobe
      r'some_ffmpeg_path\ffmpeg.exe'   # path to ffmpeg
    ),
    LayoutOptions(
      'hevc_nvenc', # Codec name
      'fast',       # Codec preset
      'pyramid',    # Layout name
      DONT_REDUCE   # Percentage value from 1-100 (or DONT_REDUCE constant)
    ),
    BaseFolderPaths(
      r'g:\TeslaCam\SentryClips',   # Path to your USB stick
      r'c:\users\user\videos\tesla' # Destination path
    ),
    True  # Keep temporary working folder
  )

if __name__ == '__main__':
  main()
```
