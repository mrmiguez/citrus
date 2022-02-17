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
    "boynton": ("dc", {'name': "custom_field",
                       'prefix': "https://dpanther.fiu.edu/sobek/content"},
                "Boynton Beach City Library Archives",
                "Florida International University Libraries"),
    'brockway': ('dc', {'name': 'custom_field',
                        'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                 'Miami Shores Village Archives at Brockway Memorial Library',
                 'Florida International University Libraries'),
    "broward": ("ssdn_mods",
                {'name': "islandora",
                 'prefix': "https://broward.digital.flvc.org/islandora/object"},
                "Broward College Archives & Special Collections", None),
    'coral_gables': ('dc', {'name': 'custom_field',
                            'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                     'City of Coral Gables',
                     'Florida International University Libraries'),
    "fau": ("ssdn_mods",
            {'name': "islandora",
             'prefix': "https://fau.digital.flvc.org/islandora/object"},
            "Florida Atlantic University", None),
    'fgcu': ('ssdn_mods', {'name': 'islandora',
                           'prefix': 'http://fgcu.digital.flvc.org/islandora/object'},
             'Florida Gulf Coast University Library', None),
    'mbvm': ('dc', {'name': 'custom_field',
                    'prefix': 'http://dpanther.fiu.edu/sobek/content'},
             'Miami Design Preservation League, Closeup Productions',
             'Florida International University Libraries'),
    ### mbvm must come before fiu, or FIU will be credited with these
    ### records instead of the Miami Design Preservation League
    ### RIP alphabet
    'fiu': ('dc', {'name': 'custom_field',
                   'prefix': 'http://dpanther.fiu.edu/sobek/content'},
            'Florida International University Libraries', None),
    'flmem': ('custom', {'name': 'web-scrape',
                         'prefix': 'https://www.floridamemory.com'},
              'Florida Memory', None),
    "fscj": ("ssdn_mods",
             {'name': "islandora",
              'prefix': "https://fscj.digital.flvc.org/islandora/object"},
             "Florida State College at Jacksonville", None),
    "ringling": ("mods", {'name': "islandora", 'prefix': "http://fsu.digital.flvc.org/islandora/object"},
                 "John and Mable Ringling Museum of Art", "Florida State University Libraries"),
    'fsu': ('mods', {'name': 'islandora',
                     'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
            'Florida State University Libraries', None),
    'gnmhs': ('dc', {'name': 'custom_field',
                     'prefix': 'http://dpanther.fiu.edu/sobek/content'},
              'Greater North Miami Historical Society',
              'Florida International University Libraries'),
    'ir_fiu': ('dcq', {'name': 'bepress', 'prefix': 'https://digitalcommons'},
               'Florida International University Libraries', None),
    'mcpl': ('dc', {'name': 'custom_field',
                    'prefix': 'http://dpanther.fiu.edu/sobek/content'},
             'Monroe County Public Library',
             'Florida International University Libraries'),
    'mdpl': ('ssdn_qdc', {'name': 'cdm', 'prefix': 'http://cdm17273.contentdm.oclc.org'},
             'Miami-Dade Public Library System', None),
    'um': ('qdc', {'name': 'cdm', 'prefix': 'http://cdm17191.contentdm.oclc.org'},
           'University of Miami Libraries', None),
    "unf": ("ssdn_dc", {'name': 'bepress', 'prefix': 'https://digitalcommons'}, "University of North Florida", None),
    'usf': ('ssdn_dc', {'name': 'custom_field', 'prefix': 'https://digital.lib.usf.edu/content'},
            'University of South Florida Libraries', None),
    'vhlf': ('dc', {'name': 'custom_field',
                    'prefix': 'http://dpanther.fiu.edu/sobek/content'},
             'Vaclav Havel Library Foundation',
             'Florida International University Libraries')
}

REPOX_EXPORT_DIR = 'D:\\Users\\Roland\\citrus_test'

OUTPUT_DIR = 'D:\\Users\\Roland\\citrus_out'

OUTPUT_FORMAT = ''

PRETTY_PRINT = True

PROVIDER = {'name': 'Sunshine State Digital Network',
            '@id': 'UNDETERMINED'}

VERBOSE = True

LOG_LEVEL = 'warn'

LOG_FILE = "citrus_errors{}.csv".format(datetime.date.today())
