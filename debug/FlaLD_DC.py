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


def write_json_ld(docs):
    with open('testData/fiu-repoxfull.json', 'w') as jsonOutput:
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
                        # need to test for ( Contributor ) and ( contributor )
                        if len(name) > 0 and "ontributor )" not in name:
                            sourceResource['creator'].append({"name": name.strip(" ") })
                        elif "ontributor )" in name:
                            if 'contributor' not in sourceResource.keys():
                                sourceResource['contributor'] = []
                                sourceResource['contributor'].append({"name": name.strip(" ").rstrip("( Contributor )").rstrip("( contributor )")})
                            else:
                                sourceResource['contributor'].append(
                                    {"name": name.strip(" ").rstrip("( Contributor )").rstrip("( contributor )")})

            # sourceResource.date
            date = OAI_QDC.simple_lookup(record, './/{0}date'.format(nameSpace_default['dc']))
            if date is not None:
                sourceResource['date'] = { "begin": date, "end": date }

            # sourceResource.description
            description = []
            if OAI_QDC.simple_lookup(record, './/{0}description'.format(nameSpace_default['dc'])) is not None:
                for item in OAI_QDC.simple_lookup(record, './/{0}description'.format(nameSpace_default['dc'])):
                    description.append(item)
            if len(description) > 1:
                sourceResource['description'] = []
                for item in description:
                    sourceResource['description'].append(item)
            elif len(description) == 1:
                sourceResource['description'] = description[0]

            # sourceResource.extent

            # sourceResource.format
            dpla_format = OAI_QDC.simple_lookup(record, './/{0}format'.format(nameSpace_default['dc']))
            if dpla_format is not None:
                sourceResource['format'] = dpla_format

            # sourceResource.genre

            # sourceResource.identifier
            dPantherPURL = re.compile('dpService/dpPurlService/purl')
            identifier = OAI_QDC.simple_lookup(record, './/{0}identifier'.format(nameSpace_default['dc']))
            if identifier is not None and len(identifier) > 1:
                sourceResource['identifier'] = []
                for ID in identifier:
                    try:
                        PURL = dPantherPURL.search(ID)
                        if PURL:
                            PURL_match = PURL.string
                        else:
                            sourceResource['identifier'].append(ID)
                    except TypeError as err:
                        with open('errorDump.txt', 'a') as dumpFile:
                            dumpFile.write('TypeError - sourceResource.identifier: {0}, {1}\n'.format(ID, err))
                            #dumpFile.write('{0}\n'.format(name))
                            dumpFile.write(etree.tostring(record).decode('utf-8'))
                        pass
            else:
                sourceResource['identifier'] = identifier

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
            place = OAI_QDC.simple_lookup(record, './/{0}coverage'.format(nameSpace_default['dc']))
            if place is not None:
                sourceResource['spatial'] = place

            # sourceResource.publisher
            publisher = OAI_QDC.simple_lookup(record, './/{0}publisher'.format(nameSpace_default['dc']))
            if publisher is not None:
                sourceResource['publisher'] = publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rights = OAI_QDC.simple_lookup(record, './/{0}rights'.format(nameSpace_default['dc']))
            if rights is not None:
                sourceResource['rights'] = rights

            # sourceResource.subject
            if OAI_QDC.simple_lookup(record, './/{0}subject'.format(nameSpace_default['dc'])) is not None:
                sourceResource['subject'] = []
                for element in OAI_QDC.split_lookup(record, './/{0}subject'.format(nameSpace_default['dc'])):
                    for term in element:
                        term = term.rstrip("( lcsh )")
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

            # aggregation.provider
            provider = {"name": "TO BE DETERMINED",
                        "@id": "DPLA provides?"}
            try:
                docs.append({"@context": "http://api.dp.la/items/context",
                             "sourceResource": sourceResource,
                             "aggregatedCHO": "#sourceResource",
                             "dataProvider": data_provider,
                             "isShownAt": PURL_match,
                             #"preview": preview, #need details on a thumbnail service
                             "provider": provider})
            except NameError as err:
                with open('errorDump.txt', 'a') as dumpFile:
                    dumpFile.write('NameError - aggregation.preview: {0}\n'.format(err))
                    # dumpFile.write('{0}\n'.format(name))
                    dumpFile.write(etree.tostring(record).decode('utf-8'))
                pass


#write_json_ld(docs) # write test
#print(json.dumps(docs, indent=2)) # dump test
