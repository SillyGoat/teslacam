import argparse

PYRAMID_LAYOUT = {
    'background_dimensions': (3840, 1920),
    # The key names below must match the file name suffixes for the camera data
    'front': (1280, 0),
    'right_repeater': (0, 960),
    'back': (1280, 960),
    'left_repeater': (2560, 960),
}


CODEC_OPTIONS = {
    'hevc_nvenc': (
        '-preset', 'slow', # slow processing
        '-b:v', '8M', # 8 MB bitrate
    ),
    'libx265': (
        '-preset', 'ultrafast', # probably faster for CPU only
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
        '--scalar',
        default=320,
        help='scalar multiplier relative to 4:3 ratio to size video to (uses more CPU)',
        type=positive_integer,
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
        dict(PYRAMID_LAYOUT),
        args.scalar,
        args.base_input_folder_path,
        args.base_output_folder_path,
        args.keep_temp_folder,
    )
