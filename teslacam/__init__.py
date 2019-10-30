' Client API and logging initialization '
import logging

from .constants import DONT_REDUCE
from .custom_types import FFMpegPaths, LayoutOptions, BaseFolderPaths
from .extract import extract_videos

# Change levels if you want to diagnose issues
logging.basicConfig(format='%(message)s', level=logging.INFO)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
