from configparser import ConfigParser
from pathlib import Path
import sys
import os

sys.path.append('.')

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = Path(__file__).parents[2]

CONFIG_FILE = '{}/config.conf'.format(PARENT_PATH)
CONFIG = ConfigParser()
CONFIG.read(CONFIG_FILE)

PATH_SAVE = CONFIG.get('PATH', 'path_data')
