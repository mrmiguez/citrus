"""
# FlaLD CONTROL VARIABLES
#
# CONFIG_DICT is the list of expected repox exports and requisite mappings
#   Keys are shortened forms of repox export directories.
#       They will be expanded by citrus-run using glob.glob(key*), so full names aren't required.
#       They should be relatively descriptive to avoid collision with other sets.
#   Values are tuples storing various run settings.
#       position 1: metadata prefix--Currently only 'dc', 'qdc', and 'mods' are supported.
#       position 2: dictionary of thumbnail service values
#       position 3: aggregation.dataProvider
#       position 4: aggregation.intermediateProvider
"""

CONFIG_DICT = {
                'um': ('qdc', {'name':'cdm', 'prefix': 'http://merrick.library.miami.edu'},
                           'University of Miami Libraries', None),
                'fiu': ('dc', {'name': 'custom_field', 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                        'Florida International University Libraries', None),
                'coral_gables': ('dc', {'name': 'custom_field', 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                        'City of Coral Gables','Florida International University Libraries'),
                'vhlf': ('dc', {'name': 'custom_field', 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                        'Vaclav Havel Library Foundation', 'Florida International University Libraries'),
                'fsu': ('mods', {'name': 'islandora', 'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
                        'Florida State University Libraries', None),
                'flmem': ('custom', {'name': 'web-scrape', 'prefix': 'https://www.floridamemory.com'},
                          'Florida Memory', None),
                'ir_fiu': ('dcq', {'name': None, 'prefix': None}, 'Florida International University Libraries', None)
}

# REPOX_EXPORT_DIR = '/home/mrmiguez/OAI_export'  # citrus_harvest dir
# REPOX_EXPORT_DIR = '/repox/export'  # repox dir
REPOX_EXPORT_DIR = 'c:\\Users\\Matthew Miguez\\citrus_test'  # local test

# OUTPUT_DIR = '~/FlaLD_JSON'
OUTPUT_DIR = 'c:\\Users\\Matthew Miguez\\citrus_out'  # local test

PRETTY_PRINT = True

PROVIDER = {'name': 'Sunshine State Digital Network',
            '@id': 'UNDETERMINED'}

VERBOSE = True
