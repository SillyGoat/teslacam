import argparse

import teslacam


def get_codec(value):
    ' Get proper codec options '
    if value not in teslacam.CODEC_OPTIONS:
        raise argparse.ArgumentTypeError(f'{value} is not a supported codec')

    return value


def valid_percent(value):
    percent = float(value)
    if percent > 0 and percent <= 100:
        return percent
    raise argparse.ArgumentTypeError(f'{value} must be a valid percent')


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
        '--preset',
        default='slow',
        help='preset to use for encoding',
    )
    parser.add_argument(
        '--reduce',
        default=teslacam.DONT_REDUCE,
        help='percent to reduce video to',
        type=valid_percent,
    )
    parser.add_argument(
        '--layout',
        default='pyramid',
        help='camera layout',
        choices=teslacam.LAYOUT_OFFSETS.keys(),
    )
    parser.add_argument(
        '--keep_temp_folder',
        default=False,
        help='keep temporary working folder after extraction',
        type=str_to_bool,
    )
    args = parser.parse_args()

    presets, number_of_parallel_encoders = teslacam.CODEC_OPTIONS[args.codec]
    if args.preset not in presets:
        quoted_choices = [f"'{x}'" for x in presets]
        parser.error(f"argument --preset: invalid choice: '{args.preset}' (choose from {', '.join(quoted_choices)})")

    layout_options = (
        args.codec,
        args.preset,
        teslacam.create_native_layout(teslacam.LAYOUT_OFFSETS[args.layout]),
        args.reduce,
    )
    return (
        args.ffmpeg_folder_path,
        number_of_parallel_encoders,
        layout_options,
        args.base_input_folder_path,
        args.base_output_folder_path,
        args.keep_temp_folder,
    )
