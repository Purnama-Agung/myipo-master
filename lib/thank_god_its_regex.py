import re

__author__ = 'P.A'


DAY_OF_WEEK = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
# =================================================================================================
#   OTHERS
# -------------------------------------------------------------------------------------------------
NUMERIC = re.compile(r'[0-9]+')
NON_NUMERIC = re.compile(r'[^0-9]+')
REMOVE_HTML_TAG = re.compile(r'<[^>]+>')
REPLACE_TAG_1 = re.compile(r'<(br/?.?|/p|/h3|/abbr|/div)>')
REMOVE_WHITE_SPACE = re.compile(r'&[^; ]+;')
REMOVE_WHITE_SPACE_2 = re.compile(r'[ ]+')
REMOVE_WHITE_SPACE_3 = re.compile(r'\n+')
REMOVE_WHITE_SPACE_4 = re.compile(r'(^\\n|\\n$)')
REMOVE_WHITE_SPACE_5 = re.compile(r'\\"')
REMOVE_WHITE_SPACE_6 = re.compile(r'\\')
REMOVE_WHITE_SPACE_7 = re.compile(r'(\')')
DATE_PATTERN_1 = re.compile(r'([0-9]+) mins?')
DATE_PATTERN_2 = re.compile(r'just now', flags=re.I)
DATE_PATTERN_3 = re.compile(r'([0-9]+) hrs?')
DATE_PATTERN_4 = re.compile(r'\byesterday at (.*)', flags=re.I)
DAY_OF_WEEK_PATTERN = re.compile(r'{}'.format('|'.join(DAY_OF_WEEK)), flags=re.I)
# =================================================================================================
