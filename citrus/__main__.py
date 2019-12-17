import os

from citrus import InternetArchive, SSDNDC, dc_standard_map, SSDNQDC, qdc_standard_map, DataProvider, DPLARecord, \
    SSDNMODS, mods_standard_map, SourceResourceRequiredElementException, SourceResource

###############################################################################
# Potential options for customizing transformation are:                       #
#   1. Sub-classing an appropriate scenario and changing the properties       #
#   2. Writing a custom map that manipulates the default scenario properties  #
#   3. Doing both                                                             #
###############################################################################


### CUSTOM MAP
def fsu_mods_map(rec):
    # sr = SourceResource()
    # sr.alternative = rec.alternative
    # sr.collection = rec.collection
    # sr.contributor = rec.contributor
    # sr.creator = rec.creator
    # sr.date = rec.date
    # sr.description = rec.description
    # sr.extent = rec.extent
    # sr.format = rec.format
    try:
        sr.identifier = rec.identifier
    except IndexError:
        pass
    # sr.language = rec.language
    # sr.place = rec.place
    # sr.publisher = rec.publisher
    try:
        sr.rights = rec.rights
    except SourceResourceRequiredElementException:
        pass
    # sr.subject = rec.subject
    return sr


### XML PARSING & SR CREATION USING SCENARIOS & MAP
IN_PATH = 'D:\\Users\\Roland\\citrus_test'
OUT_PATH = 'D:\\Users\\Roland\\citrus_out'

ORGS = [
        # ('fiu', SSDNDC, dc_standard_map, {'name': 'custom_field',
        #                                   'prefix': 'http://dpanther.fiu.edu/sobek/content'},
        #  'Florida International University Libraries', None),
        # ('usf', SSDNDC, dc_standard_map, {'name': 'custom_field', 'prefix':
        #     'https://digital.lib.usf.edu/content'},
        #  'University of South Florida Libraries', None),
        # ('um', SSDNQDC, qdc_standard_map, {'name': 'cdm', 'prefix': 'http://merrick.library.miami.edu'},
        #  'University of Miami Libraries', None),
        ('fsu', SSDNMODS, fsu_mods_map,
         {'name': 'islandora', 'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
         'Florida State University Libraries', None),
        # ('fgcu', SSDNMODS, mods_standard_map,
        #  {'name': "islandora", 'prefix': "http://fgcu.digital.flvc.org/islandora/object"},
        #  "Florida Gulf Coast University Library", None)
        ]


# ### TESTING INTERNET ARCHIVE API SCENARIO
# collection = 'statelibraryandarchivesofflorida'
#
# recs = InternetArchive(collection)
# for rec in recs:
#     print(rec.oai_id)


# ### TESTING self.harvest_id
# IN_PATH = 'D:\\Users\\Roland\\citrus_test'
#
# ORGS = [('fiu', SSDNDC, dc_standard_map, {'name': 'custom_field',
#                 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
#          'Florida International University Libraries', None),
#         ('usf', SSDNDC, dc_standard_map, {'name': 'custom_field', 'prefix':
#                      'https://digital.lib.usf.edu/content'},
#          'University of South Florida Libraries', None),
#         ('um', SSDNQDC, qdc_standard_map, {'name': 'cdm', 'prefix': 'http://merrick.library.miami.edu'},
#            'University of Miami Libraries', None)]
#
# for org in ORGS:
#     o = DataProvider()
#     o.key, o.scenario, o.map, o.thumbnail, o.data_provider, o.intermediate_provider = org
#     for f in os.listdir(os.path.join(IN_PATH, o.key)):
#         data = o.scenario(os.path.join(IN_PATH, o.key, f))
#         for sr in map(o.map, data):
#             print(sr)

if __name__ == '__main__':
    for org in ORGS:
        o = DataProvider()
        o.key, o.scenario, o.map, o.thumbnail, o.data_provider, o.intermediate_provider = org
        for f in os.listdir(os.path.join(IN_PATH, o.key)):
            data = o.scenario(os.path.join(IN_PATH, o.key, f))
            for sr in map(o.map, data):
                rec = DPLARecord()
                rec.dataProvider = o.data_provider
                rec.intermediateProvider = o.intermediate_provider
                rec.sourceResource = sr.data
                print(rec.dumps())
