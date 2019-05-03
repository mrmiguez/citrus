import datetime

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
    'coral_gables': ('dc', {'name': 'custom_field',
                            'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                     'City of Coral Gables',
                     'Florida International University Libraries'),
    'fiu': ('dc', {'name': 'custom_field',
                   'prefix': 'http://dpanther.fiu.edu/sobek/content'},
            'Florida International University Libraries', None),
    'flmem': ('custom', {'name': 'web-scrape',
                         'prefix': 'https://www.floridamemory.com'},
              'Florida Memory', None),
    'fsu': ('mods', {'name': 'islandora',
                     'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
            'Florida State University Libraries', None),
    'ir_fiu': ('dcq', {'name': None, 'prefix': None},
               'Florida International University Libraries', None),
    'mbvm': ('dc', {'name': 'custom_field',
                    'prefix': 'http://dpanther.fiu.edu/sobek/content'},
             'Miami Design Preservation League, Closeup Productions',
             'Florida International University Libraries'),
    'mcpl': ('dc', {'name': 'custom_field',
                    'prefix': 'http://dpanther.fiu.edu/sobek/content'},
             'Monroe County Public Library',
             'Florida International University Libraries'),
    'mdpl': ('ssdn_qdc', {'name': 'cdm', 'prefix': 'http://cdm17273.contentdm.oclc.org'},
             'Miami-Dade Public Library System', None),
    'um': ('qdc', {'name': 'cdm', 'prefix': 'http://merrick.library.miami.edu'},
           'University of Miami Libraries', None),
    'vhlf': ('dc', {'name': 'custom_field',
                    'prefix': 'http://dpanther.fiu.edu/sobek/content'},
             'Vaclav Havel Library Foundation',
             'Florida International University Libraries'),
    'gnmhs': ('dc', {'name': 'custom_field',
                     'prefix': 'http://dpanther.fiu.edu/sobek/content'},
              'Greater North Miami Historical Society',
              'Florida International University Libraries'),
    'usf': ('ssdn_dc', {'name': 'sobek', 'prefix': 'http://digital.lib.usf.edu/content'},
            'University of South Florida Libraries', None)

}

#REPOX_EXPORT_DIR = '/home/mrmiguez/OAI_export'
REPOX_EXPORT_DIR = 'D:\\Users\\Roland\\citrus_test'

#OUTPUT_DIR = '/home/mrmiguez/FlaLD_JSON'
OUTPUT_DIR = 'D:\\Users\\Roland\\citrus_out'

PRETTY_PRINT = True

PROVIDER = {'name': 'Sunshine State Digital Network',
            '@id': 'UNDETERMINED'}

VERBOSE = True

LOG_LEVEL = "info"

LOG_FILE = "citrus_errors{}.csv".format(datetime.date.today())
