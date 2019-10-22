import argparse


CODEC_OPTIONS = {
    'hevc_nvenc': (
        '-preset', 'slow', # slow processing
        '-b:v', '8M', # 8 MB bitrate
    ),
    'libx265': (
        '-preset', 'ultrafast', # slow processing
        '-b:v', '8M', # 8 MB bitrate
    )
}


def get_codec(value):
    ' Get proper codec options '
    if value not in CODEC_OPTIONS:
        raise argparse.ArgumentTypeError(f'{value} is not a supported codec')

    return (value, CODEC_OPTIONS[value])


def positive_integer(value):
    ' Validate positive value arguments '
    positive_value = int(value)
    if positive_value > 0:
        return positive_value
    raise argparse.ArgumentTypeError(f'{value} must be a positive integer')


def str_to_bool(value):
    ' Validate boolean arguments '
    token = value.lower()
    if token in ['true', '1']:
        return True
    elif token in ['false', '0']:
        return False
    raise argparse.ArgumentTypeError(f'{value} must be a boolean')


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ffmpeg_folder_path',
        help='full path to ffmpeg binary folder containing ffmpeg.exe and ffprobe.exe',
    )
    parser.add_argument(
        'base_input_folder_path',
        help='full path to the video folder containing dated folders',
    )
    parser.add_argument(
        'base_output_folder_path',
        help='full path of the output folder for merged files and intermediate folder',
    )
    parser.add_argument(
        '--codec',
        default='hevc_nvenc',
        help='codec to use for encoding',
        type=get_codec,
    )
    parser.add_argument(
        '--number_of_encoders',
        default=2,
        help='number of encoders to use',
        type=positive_integer,
    )
    parser.add_argument(
        '--keep_temp_folder',
        default=False,
        help='keep temporary working folder after extraction',
        type=str_to_bool,
    )
    args = parser.parse_args()
    return (
        args.ffmpeg_folder_path,
        args.number_of_encoders,
        args.codec,
        args.base_input_folder_path,
        args.base_output_folder_path,
        args.keep_temp_folder,
    )
