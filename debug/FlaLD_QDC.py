#!/usr/bin/env python3

import re
import sys
import json
import requests
from lxml import etree
from bs4 import BeautifulSoup

nameSpace_default = { None: '{http://www.loc.gov/mods/v3}',
                      'oai_dc': '{http://www.openarchives.org/OAI/2.0/oai_dc/}',
                      'dc': '{http://purl.org/dc/elements/1.1/}',
                      'mods': '{http://www.loc.gov/mods/v3}',
                      'dcterms': '{http://purl.org/dc/terms/}',
                      'xlink': '{http://www.w3.org/1999/xlink}',
                      'repox': '{http://repox.ist.utl.pt}',
                      'oai_qdc': '{http://worldcat.org/xmlschemas/qdc-1.0/}'}

IANA_type_list = []

IANA_XML = requests.get('http://www.iana.org/assignments/media-types/media-types.xml')
IANA_parsed = BeautifulSoup(IANA_XML.text, "lxml")
for type in IANA_parsed.find_all('file'):
    IANA_type_list.append(type.text)


def write_json_ld(docs):
    with open('testData/um_um-1.json', 'w') as jsonOutput:
        json.dump(docs, jsonOutput, indent=2)


class OAI_QDC:

    def __init__(self, input_file=None):
        """
        General constructor class.
        :param input_file: file or directory of files to be accessed.
        """
        if input_file is not None:
            self.input_file = input_file
            self.tree = etree.parse(self.input_file)
            self.root = self.tree.getroot()

        record_list = []

        if self.root.nsmap is not None:
            self.nsmap = self.root.nsmap

        if 'oai_dc' in self.nsmap:
            for oai_record in self.root.iterfind('.//{0}record'.format(nameSpace_default['oai_dc'])):
                #                record = OAI(oai_record)    # OOP testing
                #                record_list.append(record)  #
                record_list.append(oai_record)  # actually working line
            self.nsroot = 'oai_dc'
            self.set_spec = self.root.find('.//{0}setSpec'.format(nameSpace_default['oai_dc'])).text
            oai_id = self.root.find('.//{0}header/{0}identifier'.format(nameSpace_default['oai_dc'])).text
            oai_urn = ""
            for part in oai_id.split(':')[:-1]:
                oai_urn = oai_urn + ':' + part
            self.oai_urn = oai_urn.strip(':')

        elif 'repox' in self.nsmap:
            for oai_record in self.root.iterfind('.//{0}record'.format(nameSpace_default['repox'])):
                #                record = OAI(oai_record)    # OOP testing
                #                record_list.append(record)  #
                record_list.append(oai_record)  # actually working line
            self.nsroot = 'repox'
            self.set_spec = self.root.attrib['set']
            oai_id = self.root.find('./{0}record'.format(nameSpace_default['repox'])).attrib['id']
            oai_urn = ""
            for part in oai_id.split(':')[:-1]:
                oai_urn = oai_urn + ':' + part
            self.oai_urn = oai_urn.strip(':')

        self.record_list = record_list

    def simple_lookup(record, elem):
        if record.find('{0}'.format(elem)) is not None:
            results = []
            for item in record.findall('{0}'.format(elem)):
                results.append(item.text)
            return results

    def split_lookup(record, elem, delimiter=';'):
        if record.find('{0}'.format(elem)) is not None:
            results = []
            for item in record.findall('{0}'.format(elem)):
                results.append(item.text.split(delimiter))
            return results



with open(sys.argv[1], encoding='utf-8') as data_in:
    records = OAI_QDC(data_in)
    docs = []
    for record in records.record_list:

        if 'deleted' in record.attrib.keys():
            if record.attrib['deleted'] == 'true':
                pass

        else:

            sourceResource = {}

            # sourceResource.alternative
            alt_title = OAI_QDC.simple_lookup(record, './/{0}alternative'.format(nameSpace_default['dcterms']))
            if alt_title is not None:
                sourceResource['alternative'] = alt_title

            # sourceResource.collection

            # sourceResource.contributor
            if OAI_QDC.simple_lookup(record, './/{0}contributor'.format(nameSpace_default['dc'])) is not None:
                sourceResource['contributor'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}contributor'.format(nameSpace_default['dc'])):
                    for name in element:
                        if len(name) > 0:
                            sourceResource['contributor'].append({"name": name.strip(" ") })

            # sourceResource.creator
            if OAI_QDC.simple_lookup(record, './/{0}creator'.format(nameSpace_default['dc'])) is not None:
                sourceResource['creator'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}creator'.format(nameSpace_default['dc'])):
                    for name in element:
                        if len(name) > 0:
                            sourceResource['creator'].append({"name": name.strip(" ") })

            # sourceResource.date
            date = OAI_QDC.simple_lookup(record, './/{0}created'.format(nameSpace_default['dcterms']))
            if date is not None:
                sourceResource['date'] = { "begin": date, "end": date }

            # sourceResource.description
            description = []
            if OAI_QDC.simple_lookup(record, './/{0}description'.format(nameSpace_default['dc'])) is not None:
                for item in OAI_QDC.simple_lookup(record, './/{0}description'.format(nameSpace_default['dc'])):
                    description.append(item)
            if OAI_QDC.simple_lookup(record, './/{0}abstract'.format(nameSpace_default['dcterms'])) is not None:
                for item in OAI_QDC.simple_lookup(record, './/{0}abstract'.format(nameSpace_default['dcterms'])):
                    description.append(item)
            if len(description) > 1:
                sourceResource['description'] = []
                for item in description:
                    sourceResource['description'].append(item)
            elif len(description) == 1:
                sourceResource['description'] = description[0]

            # sourceResource.extent
            if OAI_QDC.simple_lookup(record, './/{0}extent'.format(nameSpace_default['dcterms'])) is not None:
                sourceResource['extent'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}extent'.format(nameSpace_default['dcterms'])):
                    for term in element:
                        if len(term) > 0:
                            sourceResource['extent'].append(term.strip(' '))

            # sourceResource.format

            # sourceResource.genre
            if OAI_QDC.simple_lookup(record, './/{0}format'.format(nameSpace_default['dc'])) is not None:
                sourceResource['genre'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}format'.format(nameSpace_default['dc'])):
                    for term in element:
                        if term.lower() in IANA_type_list:
                            file_format = term.lower()
                            pass
                        elif len(term) > 0:
                            sourceResource['genre'].append(term.strip(' '))
                if len(sourceResource['genre']) == 0:
                    del sourceResource['genre']

            # sourceResource.identifier
            local_id = OAI_QDC.simple_lookup(record, './/{0}identifier'.format(nameSpace_default['dc']))
            if local_id is not None:
                sourceResource['identifier'] = local_id[0]

            # sourceResource.language
            if OAI_QDC.simple_lookup(record, './/{0}language'.format(nameSpace_default['dc'])) is not None:
                sourceResource['language'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}language'.format(nameSpace_default['dc'])):
                    for term in element:
                        if len(term) > 3:
                            sourceResource['language'] = {"name": term }
                        else:
                            sourceResource['language'] = { "iso_639_3": term }

            # sourceResource.place : sourceResource['spatial']
            if OAI_QDC.simple_lookup(record, './/{0}spatial'.format(nameSpace_default['dcterms'])) is not None:
                sourceResource['spatial'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}spatial'.format(nameSpace_default['dcterms'])):
                    for term in element:
                        if len(term) > 0:
                            sourceResource['spatial'].append(term.strip(' '))

            # sourceResource.publisher
            publisher = OAI_QDC.simple_lookup(record, './/{0}publisher'.format(nameSpace_default['dc']))
            if publisher is not None:
                sourceResource['publisher'] = publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rightsURI = re.compile('http://rightsstatements')
            if OAI_QDC.simple_lookup(record, './/{0}rights'.format(nameSpace_default['dc'])) is not None:
                if len(record.findall('.//{0}rights'.format(nameSpace_default['dc']))) > 1:
                    for rights_statement in OAI_QDC.simple_lookup(record, './/{0}rights'.format(nameSpace_default['dc'])):
                        URI = rightsURI.search(rights_statement)
                        if URI:
                            URI_match = URI.string.split(" ")[-1]
                        else:
                            rights_text = rights_statement
                    sourceResource['rights'] = { "@id": URI_match, "text": rights_text }
                else:
                    sourceResource['rights'] = OAI_QDC.simple_lookup(record, './/{0}rights'.format(nameSpace_default['dc']))

            # sourceResource.subject
            if OAI_QDC.simple_lookup(record, './/{0}subject'.format(nameSpace_default['dc'])) is not None:
                sourceResource['subject'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}subject'.format(nameSpace_default['dc'])):
                    for term in element:
                        if len(term) > 0:
                            sourceResource['subject'].append({"name": term.strip(" ") })

            # sourceResource.title
            title = OAI_QDC.simple_lookup(record, './/{0}title'.format(nameSpace_default['dc']))
            if title is not None:
                sourceResource['title'] = title

            # sourceResource.type
            if OAI_QDC.simple_lookup(record, './/{0}type'.format(nameSpace_default['dc'])) is not None:
                sourceResource['type'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}type'.format(nameSpace_default['dc'])):
                    for term in element:
                        if len(term) > 0:
                            sourceResource['type'].append(term.strip(" "))

            # webResource.fileFormat

            # aggregation.dataProvider
            data_provider = "temp"

            # aggregation.isShownAt

            # aggregation.preview
            collectionID = local_id[0].split('/')[6]
            itemID = local_id[0].split('/')[8]
            cdm_url_prefix = { 'um': 'http://merrick.library.miami.edu' }
            cdm_url_path = '/utils/getthumbnail/collection/{0}/id/{1}'.format(collectionID, itemID)

            if "merrick.library.miami.edu" in local_id[0]:
                preview = cdm_url_prefix['um'] + cdm_url_path

            # aggregation.provider
            provider = {"name": "TO BE DETERMINED",
                        "@id": "DPLA provides?"}

            docs.append({"@context": "http://api.dp.la/items/context",
                         "sourceResource": sourceResource,
                         "aggregatedCHO": "#sourceResource",
                         "dataProvider": data_provider,
                         "isShownAt": local_id[0],
                         "preview": preview,
                         "provider": provider})

#write_json_ld(docs) # write test
# print(json.dumps(docs, indent=2)) # dump test
