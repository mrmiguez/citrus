import datetime
import os
import logging

import sickle
from sickle import models
from sickle.iterator import OAIItemIterator
from sickle.utils import xml_to_dict


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SickleRecord(models.Record):

    def __init__(self, record_element, strip_ns=True):
        models.Record.__init__(self, record_element, strip_ns=strip_ns)

    def get_metadata(self):
        try:
            self.metadata = xml_to_dict(
                self.xml.find(
                    './/' + self._oai_namespace + 'metadata'
                ).getchildren()[0], strip_ns=self._strip_ns)
        except AttributeError:
            self.metadata = None


def harvest(harvest_info, section, write_path, verbosity):
    # check for dir path
    if not os.path.exists(os.path.join(write_path, section)):
        os.makedirs(os.path.join(write_path, section))

    # OAI-PMH endpoint URL from config
    oai = harvest_info['OAIEndpoint']

    # metadataPrefix from config
    metadata_prefix = harvest_info['MetadataPrefix']

    # iterate through sets to harvest
    for set_spec in harvest_info['SetList'].split(', '):
        if verbosity > 1:
            print(f'Harvesting {section} set {set_spec}')

        # Sickle harvester
        harvester = sickle.Sickle(oai, iterator=OAIItemIterator, encoding='utf-8')
        harvester.class_mapping['ListRecords'] = SickleRecord

        records = harvester.ListRecords(set=set_spec, metadataPrefix=metadata_prefix, ignore_deleted=True)

        # write XML
        with open(os.path.join(write_path, section, f'{set_spec.replace(":", "_")}_{datetime.date.today()}.xml'), 'w',
                  encoding='utf-8') as fp:
            fp.write('<oai>')
            for record in records:
                fp.write(record.raw)
            fp.write('</oai>')
