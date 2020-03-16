import datetime
import os

from sickle import Sickle
from sickle.iterator import OAIItemIterator


def harvest(harvest_info, section, write_path):

    # check for dir path
    if not os.path.exists(os.path.join(write_path, section)):
        os.makedirs(os.path.join(write_path, section))

    # OAI-PMH endpoint URL from config
    oai = harvest_info['OAIEndpoint']

    # metadataPrefix from config
    metadata_prefix = harvest_info['MetadataPrefix']

    # iterate through sets to harvest
    for set_spec in harvest_info['SetList'].split(', '):

        # Sickle harvester
        harvester = Sickle(oai, iterator=OAIItemIterator)
        records = harvester.ListRecords(set=set_spec, metadataPrefix=metadata_prefix, ignore_deleted=True)

        # write XML
        with open(os.path.join(write_path, section, f'{set_spec}_{datetime.date.today()}.xml'), 'w') as fp:
            fp.write('<oai>')
            for record in records:
                fp.write(record.raw)
            fp.write('</oai>')
