import os
from configparser import ConfigParser

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = '{}/config.conf'.format(CURRENT_DIR)
CF = ConfigParser()
CF.read(CONFIG)

PATH_SAVE = CF.get('PATH', 'path_data')

BEANSTALK_HOST = CF.get('BEANSTALK', 'host')
TUBE_PREF = CF.get('TUBE', 'prefix')
TUBE_INDEX = '{}_{}'.format(TUBE_PREF, CF.get('TUBE', 'index'))
