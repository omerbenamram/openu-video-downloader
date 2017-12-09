import os
from pathlib import Path
import tempfile

OPENU_HOME = 'https://opal.openu.ac.il/'
OPENU_LOGIN_PAGE = 'https://sso.apps.openu.ac.il/SheiltaPortalLogin?T_PLACE=https://sheilta.apps.openu.ac.il/pls/dmyopt2/sheilta.main'

MAX_CONCURRENT_DOWNLOADS = 5
MAX_RETRIES = 5
RETRY_DURATION = 60

DEFAULT_OUTPUT_DIRECTORY = Path(os.path.expanduser('~')).joinpath('ArtistWorks')
LOG_PATH = Path(tempfile.gettempdir()).joinpath('artistworks_downloader.log')
OPENU_VIDEO_COLLECTION_TEMPLATE = 'https://opal.openu.ac.il/mod/ouilvideocollection/view.php?id={collection_id}'
