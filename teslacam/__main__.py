' Main entry point file '
import logging
import pathlib
import sys
import timeit

def initialize_logger(logger, formatter, log_level):
    ' Initializes specified logger with log level '
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    assert not logger.hasHandlers()
    logger.addHandler(handler)
    logger.setLevel(log_level)

def main():
    ' Main entry point '
    asyncio_formatter = logging.Formatter(
        fmt='[%(asctime)s: %(name)s - %(levelname)s]: %(message)s',
        datefmt='%H:%M:%S'
    )
    initialize_logger(
        logging.getLogger('asyncio'),
        asyncio_formatter,
        logging.WARNING
    )

    # Inject the local teslacam code into sys.path to allow us to
    # debug and develop teslacam while the actual teslacam module is installed
    import_path = str(pathlib.Path(__file__).parent.parent)
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

    # Warning is disabled here because we are separating local module development
    # from installed module usage
    # __main__.py is special in that we can't use relative importing
    # (e.g. from . import *)
    #pylint: disable=import-outside-toplevel
    from teslacam import (
        arg_parser,
        constants,
        extract,
        time_duration
    )

    log_level, extract_videos_arguments = arg_parser.get_arguments()
    logger = logging.getLogger(constants.LOGGER_NAME)
    teslacam_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    initialize_logger(logger, teslacam_formatter, log_level)
    def _extract_videos():
        try:
            extract.extract_videos(*extract_videos_arguments)
        except KeyboardInterrupt:
            pass

    execution_time = timeit.timeit(
        _extract_videos,
        setup='gc.enable()', # Re-enable garbage collection
        number=1
    )
    duration = time_duration.seconds_to_units(execution_time)
    logger.info('execution time: %s', duration)

main()
