' Main entry point file '
import os
import sys
import timeit

def main():
    ' Main entry point '
    import_path = os.path.split(os.path.split(__file__)[0])[0]
    if import_path not in sys.path:
        sys.path.append(import_path)

    from teslacam import arg_parser
    from teslacam import extract
    from teslacam import time_duration

    extract_videos_arguments = arg_parser.get_arguments()
    execution_time = timeit.timeit(
        lambda: extract.extract_videos(*extract_videos_arguments),
        setup='gc.enable()', # Re-enable garbage collection
        number=1
    )
    duration = time_duration.seconds_to_units(execution_time)
    print(f'Completed in {duration}')

main()
