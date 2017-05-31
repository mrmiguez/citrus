#!/usr/bin/env python3

import re
import sys
import json
import requests
from pymods import OAIReader
from bs4 import BeautifulSoup

PROVIDER = 'FSU'  # temp
dprovide = 'FSU'  # temp

nameSpace_default = { None: '{http://www.loc.gov/mods/v3}',
                      'oai_dc': '{http://www.openarchives.org/OAI/2.0/oai_dc/}',
                      'dc': '{http://purl.org/dc/elements/1.1/}',
                      'mods': '{http://www.loc.gov/mods/v3}',
                      'dcterms': '{http://purl.org/dc/terms/}',
                      'xlink': '{http://www.w3.org/1999/xlink}',
                      'repox': '{http://repox.ist.utl.pt}',
                      'oai_qdc': '{http://worldcat.org/xmlschemas/qdc-1.0/}'}

dc = nameSpace_default['dc']
dcterms = nameSpace_default['dcterms']

IANA_type_list = []

IANA_XML = requests.get('http://www.iana.org/assignments/media-types/media-types.xml')
IANA_parsed = BeautifulSoup(IANA_XML.text, "lxml")
for type in IANA_parsed.find_all('file'):
    IANA_type_list.append(type.text)


def write_json_ld(docs):
    with open('testData/um_um-1.json', 'w') as jsonOutput:
        json.dump(docs, jsonOutput, indent=2)


with open(sys.argv[1], encoding='utf-8') as data_in:
    records = OAIReader(data_in)
    docs = []
    for record in records:

        if 'deleted' in record.attrib.keys():
            if record.attrib['deleted'] == 'true':
                pass

        else:
            oai_id = record.oai_urn

            sourceResource = {}

            # sourceResource.alternative
            alt_title = record.metadata.get_element('.//{0}alternative'.format(dcterms))
            if alt_title:
                sourceResource['alternative'] = alt_title

            # sourceResource.collection

            # sourceResource.contributor
            if record.metadata.get_element('.//{0}contributor'.format(dc)):
                sourceResource['contributor'] = record.metadata.get_element('.//{0}contributor'.format(dc), delimiter=';')

            # sourceResource.creator
            if record.metadata.get_element('.//{0}creator'.format(dc)):
                sourceResource['creator'] = record.metadata.get_element('.//{0}creator'.format(dc), delimiter=';')

            # sourceResource.date
            date = record.metadata.get_element('.//{0}created'.format(dcterms))
            if date is not None:
                sourceResource['date'] = {"begin": date[0], "end": date[0]}

            # sourceResource.description
            description = []
            if record.metadata.get_element('.//{0}description'.format(dc)) is not None:
                for item in record.metadata.get_element('.//{0}description'.format(dc)):
                    description.append(item)
            if record.metadata.get_element('.//{0}abstract'.format(dcterms)) is not None:
                for item in record.metadata.get_element('.//{0}abstract'.format(dcterms)):
                    description.append(item)
            if len(description) > 1:
                sourceResource['description'] = []
                for item in description:
                    sourceResource['description'].append(item)
            elif len(description) == 1:
                sourceResource['description'] = description[0]

            # sourceResource.extent
            if record.metadata.get_element('.//{0}extent'.format(dcterms)):
                sourceResource['extent'] = record.metadata.get_element('.//{0}extent'.format(dcterms), delimiter=';')

            # sourceResource.format

            # sourceResource.genre
            if record.metadata.get_element('.//{0}format'.format(dc)):
                sourceResource['genre'] = []
                for element in record.metadata.get_element('.//{0}format'.format(dc), delimiter=';'):
                    if element.lower() in IANA_type_list:
                        file_format = element.lower()
                        pass
                    elif len(element) > 0:
                        sourceResource['genre'].append(element.strip(' '))
                if len(sourceResource['genre']) == 0:
                    del sourceResource['genre']

            # sourceResource.identifier
            local_id = record.metadata.get_element('.//{0}identifier'.format(dc))
            if local_id:
                sourceResource['identifier'] = local_id

            # sourceResource.language
            if record.metadata.get_element('.//{0}language'.format(dc)):
                sourceResource['language'] = []
                for element in record.metadata.get_element('.//{0}language'.format(dc), delimiter=';'):
                    if len(element) > 3:
                        sourceResource['language'] = {"name": element}
                    else:
                        sourceResource['language'] = {"iso_639_3": element}

            # sourceResource.place : sourceResource['spatial']
            if record.metadata.get_element('.//{0}spatial'.format(dcterms)):
                sourceResource['spatial'] = record.metadata.get_element('.//{0}spatial'.format(dcterms), delimiter=';')

            # sourceResource.publisher
            publisher = record.metadata.get_element('.//{0}publisher'.format(dc))
            if publisher:
                sourceResource['publisher'] = publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rightsURI = re.compile('http://rightsstatements')
            if record.metadata.get_element('.//{0}rights'.format(dc)):
                if len(record.metadata.findall('.//{0}rights'.format(dc))) > 1:
                    for rights_statement in record.metadata.get_element('.//{0}rights'.format(dc)):
                        URI = rightsURI.search(rights_statement)
                        if URI:
                            URI_match = URI.string.split(" ")[-1]
                        else:
                            rights_text = rights_statement
                    sourceResource['rights'] = {"@id": URI_match, "text": rights_text}
                else:
                    sourceResource['rights'] =record.metadata.get_element('.//{0}rights'.format(dc))

            # else:  # TODO re-enable logging
            #     logging.warning('No sourceResource.rights - {0}'.format(oai_id))
            #     continue

            # sourceResource.subject
            if record.metadata.get_element('.//{0}subject'.format(dc)):
                sourceResource['subject'] = record.metadata.get_element('.//{0}subject'.format(dc), delimiter=';')

            # sourceResource.title
            title = record.metadata.get_element('.//{0}title'.format(dc))
            if title is not None:
                sourceResource['title'] = title
            # else:  # TODO re-enable logging
            #     logging.warning('No sourceResource.title - {0}'.format(oai_id))
            #     continue

            # sourceResource.type
            if record.metadata.get_element('.//{0}type'.format(dc)):
                sourceResource['type'] = record.metadata.get_element('.//{0}type'.format(dc), delimiter=';')

            # webResource.fileFormat

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # # aggregation.preview  # TODO - re-enable tn service
            # for identifier in local_id:
            #     if 'http' in identifier:
            #         is_shown_at = identifier
            #         preview = assets.thumbnail_service(identifier, tn)

            # aggregation.provider

            docs.append({"@context": "http://api.dp.la/items/context",
                         "sourceResource": sourceResource,
                         "aggregatedCHO": "#sourceResource",
                         "dataProvider": data_provider,
                         #"isShownAt": is_shown_at,
                         #"preview": preview,
                         "provider": PROVIDER})

#write_json_ld(docs) # write test
print(json.dumps(docs, indent=2)) # dump test
