from sickle import Sickle
from sickle.iterator import OAIResponseIterator
import os
import datetime

###################################################
#                                                 #
# Some options for harvest include:               #
#   1. customizing Sickle to work with QDC & MODS #
#   2. rewriting pyoaiharver to python3           #
#                                                 #
###################################################


def harvest(citrus_config, harvest_parser):
    WRITE_PATH = os.path.abspath(citrus_config['ssdn']['InFilePath'])
    for section, options in harvest_parser.items():

        # skip auto generated DEFAULT config section
        if section != 'DEFAULT':
            # check for dir path
            if not os.path.exists(os.path.join(WRITE_PATH, section)):
                os.makedirs(os.path.join(WRITE_PATH, section))
            # OAI-PMH endpoint URL from config
            oai = options['OAIEndpoint']
            # metadataPrefix from config
            metadata_prefix = options['MetadataPrefix']
            # iterate through sets to harvest
            for set_spec in options['SetList'].split(', '):
                # Sickle harvester
                harvester = Sickle(oai, iterator=OAIResponseIterator)
                # XML records, note ignore_deleted isn't working
                #    might need to subclass Sickle
                records = harvester.ListRecords(set=set_spec, metadataPrefix=metadata_prefix, ignore_deleted=True)
                # write XML
                with open(os.path.join(WRITE_PATH, section, f'{set_spec}_{datetime.date.today()}.xml'), 'wb') as fp:
                    fp.write(records.next().raw.encode('utf-8'))
