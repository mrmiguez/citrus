import logging
import re

import requests
import dateparser
from bs4 import BeautifulSoup
from pymods import OAIReader

# custom functions and variables
import assets
from citrus_config import VERBOSE

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

logger = logging.getLogger(__name__)


def SSDN_QDC(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        records = OAIReader(data_in)
        docs = []
        for record in records:

            # deleted record handling for repox
            try:
                if 'deleted' in record.attrib.keys():
                    if record.attrib['deleted'] == 'true':
                        continue
            except AttributeError:
                pass

            # deleted record handling for OAI-PMH
            try:
                if 'status' in record.find('./{*}header').attrib.keys():
                    if record.find('./{*}header').attrib['status'] == 'deleted':
                        continue
            except AttributeError:
                pass

            oai_id = record.oai_urn

            if VERBOSE:
                print(oai_id)
            logger.debug(oai_id)
            sourceResource = {}

            # sourceResource.alternative
            alt_title = record.metadata.get_element(
                './/{0}alternative'.format(dcterms))
            if alt_title:
                sourceResource['alternative'] = alt_title

            # sourceResource.collection
            if record.metadata.get_element('.//{0}isPartOf'.format(dcterms)):
                sourceResource['collection'] = record.metadata.get_element('.//{0}isPartOf'.format(dcterms))

            # sourceResource.contributor
            if record.metadata.get_element('.//{0}contributor'.format(dc)):
                sourceResource['contributor'] = [{"name": name}
                                                 for name in
                                                 record.metadata.get_element(
                                                     './/{0}contributor'.format(dc),
                                                     delimiter=';')]

            # sourceResource.creator
            if record.metadata.get_element('.//{0}creator'.format(dc)):
                sourceResource['creator'] = []
                for name in record.metadata.get_element('.//{0}creator'.format(dc),
                                                        delimiter=';'):
                    # need to test for ( Contributor ) and ( contributor )
                    if (len(name) > 0) and ("ontributor )" not in name):
                        sourceResource['creator'].append({"name": name.strip(" ")})
                    elif "ontributor )" in name:
                        if 'contributor' not in sourceResource.keys():
                            sourceResource['contributor'] = []
                            sourceResource['contributor'].append({"name": name.strip(
                                " ").rstrip("( Contributor )").rstrip(
                                "( contributor )")})
                        else:
                            sourceResource['contributor'].append(
                                {"name": name.strip(" ").rstrip(
                                    "( Contributor )").rstrip("( contributor )")})

            # sourceResource.date
            date = record.metadata.get_element('.//{0}created'.format(dcterms))
            if date is None:  # TODO: there has to be a better way to do this
                date = record.metadata.get_element('.//{0}issued'.format(dcterms))
            if date is None:
                date = record.metadata.get_element('.//{0}date'.format(dcterms))
            if date is None:
                date = record.metadata.get_element('.//{0}date'.format(dc))
            if date is None:
                date = record.metadata.get_element('.//{0}available'.format(dcterms))
            if date is None:
                date = record.metadata.get_element('.//{0}dateAccepted'.format(dcterms))
            if date is None:
                date = record.metadata.get_element('.//{0}dateCopyrighted'.format(dcterms))
            if date is None:
                date = record.metadata.get_element('.//{0}dateSubmitted'.format(dcterms))

            if date is not None:
                sourceResource['date'] = {"begin": date[0], "end": date[0], "displayDate": date[0]}

            # sourceResource.description
            description = []
            if record.metadata.get_element(
                    './/{0}description'.format(dc)) is not None:
                for item in record.metadata.get_element(
                        './/{0}description'.format(dc)):
                    description.append(item)
            if record.metadata.get_element(
                    './/{0}abstract'.format(dcterms)) is not None:
                for item in record.metadata.get_element(
                        './/{0}abstract'.format(dcterms)):
                    description.append(item)
            if description:
                sourceResource['description'] = description

            # sourceResource.extent
            if record.metadata.get_element('.//{0}extent'.format(dcterms)):
                sourceResource['extent'] = record.metadata.get_element(
                    './/{0}extent'.format(dcterms), delimiter=';')

            # sourceResource.format
            if record.metadata.get_element('.//{0}medium'.format(dcterms)):
                sourceResource['format'] = []
                for element in record.metadata.get_element('.//{0}medium'.format(dcterms),
                                                           delimiter=';'):
                    if element.lower() in IANA_type_list:
                        file_format = element.lower()
                        pass
                    elif len(element) > 0:
                        sourceResource['format'].append({'name': element.strip(' ')})
                if len(sourceResource['format']) == 0:
                    del sourceResource['format']

            # sourceResource.genre

            # sourceResource.identifier
            sourceResource['identifier'] = oai_id

            # sourceResource.language
            if record.metadata.get_element('.//{0}language'.format(dc)):
                sourceResource['language'] = []
                for element in record.metadata.get_element(
                        './/{0}language'.format(dc), delimiter=';'):
                    if len(element) > 3:
                        sourceResource['language'].append({"name": element})
                    else:
                        sourceResource['language'].append({"iso_639_3": element})

            # sourceResource.place : sourceResource['spatial']
            if record.metadata.get_element('.//{0}spatial'.format(dcterms)):
                for place in record.metadata.get_element('.//{0}spatial'.format(dcterms), delimiter=';'):
                    try:
                        float(place)
                    except ValueError:
                        sourceResource['spatial'] = [place]

            # sourceResource.publisher
            publisher = record.metadata.get_element('.//{0}publisher'.format(dc))
            if publisher:
                sourceResource['publisher'] = publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rights_uri = re.compile('http://rightsstatements')
            if record.metadata.get_element('.//{0}rights'.format(dc)):
                for rights_statement in record.metadata.get_element(
                        './/{0}rights'.format(dc)):
                    uri = rights_uri.search(rights_statement)
                    if uri:
                        sourceResource['rights'] = [{"@id": uri.string.strip()}]
                        break
                    else:
                        sourceResource['rights'] = [{"text": rights_statement.strip()}]

            else:
                logger.error('No sourceResource.rights - {0}'.format(oai_id))
                continue

            # sourceResource.subject
            if record.metadata.get_element('.//{0}subject'.format(dc)):
                sourceResource['subject'] = [{"name": name}
                                             for name in record.metadata.get_element(
                        './/{0}subject'.format(dc), delimiter=';')]

            # sourceResource.temporal
            temporal = record.metadata.get_element('.//{0}temporal'.format(dcterms))
            if temporal:
                sourceResource['temporal'] = temporal

            # sourceResource.title
            title = record.metadata.get_element('.//{0}title'.format(dc))
            if title is not None:
                sourceResource['title'] = title
            else:
                logger.error('No sourceResource.title - {0}'.format(oai_id))
                continue

            # sourceResource.type
            if record.metadata.get_element('.//{0}type'.format(dc)):
                sourceResource['type'] = record.metadata.get_element(
                    './/{0}type'.format(dc), delimiter=';')

            # webResource.fileFormat
            #  TODO: file_format kicked out of SR.genre

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            for identifier in record.metadata.get_element('.//{0}identifier'.format(dc)):
                if 'http' in identifier:
                    is_shown_at = identifier
                    preview = assets.thumbnail_service(identifier, tn)

            # aggregation.provider

            doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)

            try:
                docs.append(doc)
            except UnboundLocalError:
                continue

    return docs


def SSDN_DC(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        records = OAIReader(data_in)
        docs = []
        for record in records:

            # deleted record handling for repox
            try:
                if 'deleted' in record.attrib.keys():
                    if record.attrib['deleted'] == 'true':
                        continue
            except AttributeError:
                pass

            # deleted record handling for OAI-PMH
            try:
                if 'status' in record.find('./{*}header').attrib.keys():
                    if record.find('./{*}header').attrib['status'] == 'deleted':
                        continue
            except AttributeError:
                pass

            oai_id = record.oai_urn

            if VERBOSE:
                print(oai_id)
            logger.debug(oai_id)
            sourceResource = {}

            # sourceResource.alternative

            # sourceResource.collection
            if record.metadata.get_element('.//{0}relation'.format(dc)):
                sourceResource['collection'] = record.metadata.get_element('.//{0}relation'.format(dc))

            # sourceResource.contributor
            if record.metadata.get_element('.//{0}contributor'.format(dc)):
                sourceResource['contributor'] = [{"name": name}
                                                 for name in
                                                 record.metadata.get_element(
                                                     './/{0}contributor'.format(dc),
                                                     delimiter=';')]

            # sourceResource.creator
            if record.metadata.get_element('.//{0}creator'.format(dc)):
                sourceResource['creator'] = []
                for name in record.metadata.get_element('.//{0}creator'.format(dc),
                                                        delimiter=';'):
                    # need to test for ( Contributor ) and ( contributor )
                    if (len(name) > 0) and ("ontributor )" not in name):
                        sourceResource['creator'].append({"name": name.strip(" ")})
                    elif "ontributor )" in name:
                        if 'contributor' not in sourceResource.keys():
                            sourceResource['contributor'] = []
                            sourceResource['contributor'].append({"name": name.strip(
                                " ").rstrip("( Contributor )").rstrip(
                                "( contributor )")})
                        else:
                            sourceResource['contributor'].append(
                                {"name": name.strip(" ").rstrip(
                                    "( Contributor )").rstrip("( contributor )")})

            # sourceResource.date
            date = record.metadata.get_element('.//{0}date'.format(dc))
            if date:
                d = dateparser.parse(date[0], languages=['en']).date().isoformat()
                sourceResource['date'] = {"begin": d, "end": d, "displayDate": d}

            # sourceResource.description
            if record.metadata.get_element('.//{0}description'.format(dc)):
                sourceResource['description'] = record.metadata.get_element(
                    './/{0}description'.format(dc), delimiter=';')

            # sourceResource.extent

            # sourceResource.format
            if record.metadata.get_element('.//{0}format'.format(dc)):
                sourceResource['format'] = record.metadata.get_element(
                    './/{0}format'.format(dc))

            # sourceResource.genre

            # sourceResource.identifier
            sourceResource['identifier'] = oai_id

            # sourceResource.language
            if record.metadata.get_element('.//{0}language'.format(dc)):
                sourceResource['language'] = []
                for lang in record.metadata.get_element('.//{0}language'.format(dc), delimiter=';'):
                    sourceResource['language'].append(lang)

            # sourceResource.place : sourceResource['spatial']
            if record.metadata.get_element('.//{0}coverage'.format(dc)):
                sourceResource['spatial'] = [{'name': place}
                                             for place in
                                             record.metadata.get_element(
                                                 './/{0}coverage'.format(dc))]

            # sourceResource.publisher
            publisher = record.metadata.get_element('.//{0}publisher'.format(dc))
            if publisher:
                sourceResource['publisher'] = publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rights_uri = re.compile('http://rightsstatements')
            if record.metadata.get_element('.//{0}rights'.format(dc)):
                for rights_statement in record.metadata.get_element(
                        './/{0}rights'.format(dc)):
                    uri = rights_uri.search(rights_statement)
                    if uri:
                        sourceResource['rights'] = [{"@id": uri.string.strip()}]
                        break
                    else:
                        sourceResource['rights'] = [{"text": rights_statement.strip()}]

            else:
                logger.error('No sourceResource.rights - {0}'.format(oai_id))
                continue

            # sourceResource.subject
            if record.metadata.get_element('.//{0}subject'.format(dc)):
                sourceResource['subject'] = []
                for term in record.metadata.get_element('.//{0}subject'.format(dc),
                                                        delimiter=';'):
                    term = re.sub("\( lcsh \)$", '', term)
                    if len(term) > 0:
                        sourceResource['subject'].append({"name": term.strip(". ")})

            # sourceResource.temporal

            # sourceResource.title
            title = record.metadata.get_element('.//{0}title'.format(dc))
            if title is not None:
                sourceResource['title'] = title
            else:
                logger.error('No sourceResource.title - {0}'.format(oai_id))
                continue

            # sourceResource.type
            if record.metadata.get_element('.//{0}type'.format(dc)):
                sourceResource['type'] = record.metadata.get_element(
                    './/{0}type'.format(dc), delimiter=';')

            # webResource.fileFormat
            #  TODO: file_format kicked out of SR.genre

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            for identifier in record.metadata.get_element('.//{0}identifier'.format(dc)):
                if 'http' in identifier:
                    is_shown_at = identifier
            preview = assets.thumbnail_service(record.metadata.get_element('.//{0}identifier'.format(dc)), tn)

            # aggregation.provider

            # build record

            doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)

            try:
                docs.append(doc)
            except UnboundLocalError:
                continue

    return docs
