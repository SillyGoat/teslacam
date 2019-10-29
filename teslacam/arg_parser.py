' Argument parser '
import argparse

from . import constants
from . import custom_types

def valid_percent(value):
    ' Validate percentage values '
    percent = float(value)
    if 0 < percent <= 100:
        return percent
    raise argparse.ArgumentTypeError(f'{value} must be within 1 and 100')


def str_to_bool(value):
    ' Validate boolean arguments '
    token = value.lower()
    true_values = ['t', 'true', '1']
    if token in true_values:
        return True

    false_values = ['f', 'false', '0']
    if token in false_values:
        return False

    quoted_choices = ', '.join([f"'{choice}'" for choice in true_values + false_values])
    raise argparse.ArgumentTypeError(f"invalid choice '{value}' (choose from {quoted_choices})")


def get_arguments():
    ' Parse command line arguments '
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ffprobe_file_path',
        help='full path to ffprobe binary',
    )
    parser.add_argument(
        'ffmpeg_file_path',
        help='full path to ffmpeg binary',
    )
    parser.add_argument(
        'input_folder_path',
        help='full path to the video folder containing timestamped folders',
    )
    parser.add_argument(
        'output_folder_path',
        help='full path of the output folder for merged files and temporary work folder',
    )
    parser.add_argument(
        '--codec',
        default='hevc_nvenc',
        help='codec to use for encoding',
        choices=constants.CODEC_OPTIONS.keys(),
    )
    parser.add_argument(
        '--preset',
        default='slow',
        help='preset to use for encoding',
    )
    parser.add_argument(
        '--reduce',
        default=constants.DONT_REDUCE,
        help='percent to reduce video to',
        type=valid_percent,
    )
    parser.add_argument(
        '--layout',
        default='pyramid',
        help='camera layout',
        choices=constants.LAYOUT_OFFSETS.keys(),
    )
    parser.add_argument(
        '--keep_temp_folder',
        default=False,
        help='keep temporary working folder after extraction',
        type=str_to_bool,
    )
    args = parser.parse_args()

    presets, _ = constants.CODEC_OPTIONS[args.codec]
    if args.preset not in presets:
        quoted_choices = ', '.join([f"'{x}'" for x in presets])
        parser.error(
            f"argument --preset: invalid choice: '{args.preset}' (choose from {quoted_choices})"
        )

    return (
        custom_types.FFMpegPaths(
            args.ffprobe_file_path,
            args.ffmpeg_file_path,
        ),
        custom_types.LayoutOptions(
            args.codec,
            args.preset,
            args.layout,
            args.reduce,
        ),
        custom_types.BaseFolderPaths(
            args.input_folder_path,
            args.output_folder_path,
        ),
        args.keep_temp_folder,
    )
