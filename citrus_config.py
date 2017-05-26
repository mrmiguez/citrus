"""
# FlaLD CONTROL VARIABLES
#
# CONFIG_DICT is the list of expected repox exports and requisite mappings
#   Keys are shortened forms of repox export directories.
#       They will be expanded by runFlaLD using glob.glob(key*), so full names aren't required.
#       They should be relatively descriptive to avoid collision with other sets.
#   Values are tuples storing various run settings.
#       position 1: metadata prefix--Currently only 'dc', 'qdc', and 'mods' are supported.
#       position 2: dictionary of thumbnail service values
#       position 3: aggregation.dataProvider
#       position 4: aggregation.intermediateProvider
"""

CONFIG_DICT = { 'umiami': ('qdc', {'name':'cdm', 'prefix': 'http://merrick.library.miami.edu'},
                           'University of Miami-TEMP', None),
                'fiu': ('dc', {'name': 'sobek', 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                        'Florida International University-TEMP', 'University of Miami-TEMP'),
                'fsu': ('mods', {'name': 'islandora', 'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
                        'Florida State University Libraries', None) }

# REPOX_EXPORT_DIR = '/repox/export'
REPOX_EXPORT_DIR = 'name_tests' # local test

# OUTPUT_DIR = '~/FlaLD_JSON'
OUTPUT_DIR = '' # local test

PRETTY_PRINT = True

PROVIDER = {'name': 'Florida State University Libraries',
            '@id': 'UNDETERMINED'}
