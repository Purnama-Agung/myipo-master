from configparser import ConfigParser
import sys
import os

sys.path.append('.')
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, os.pardir))

CONFIG_FILE = '{}/config.conf'.format(PARENT_PATH)
CONFIG = ConfigParser()
CONFIG.read(CONFIG_FILE)

PATH_SAVE = CONFIG.get('PATH', 'path_data')
