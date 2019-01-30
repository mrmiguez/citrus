import logging
import re

import requests
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


def FlaLD_DC(file_in, tn, dprovide, iprovide=None):
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
                sourceResource['date'] = {"begin": date[0], "end": date[0], "displayDate": date[0]}

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
            dPantherPURL = re.compile('http://dpanther.fiu.edu/dpService/dpPurlService')
            dPantherURL = re.compile('http://dpanther')
            identifier = record.metadata.get_element('.//{0}identifier'.format(dc))
            try:
                for ID in identifier:
                    if dPantherPURL.search(ID):
                        PURL_match = ID
                        sourceResource['identifier'] = ID
                        break
                    elif dPantherURL.search(ID):
                        sourceResource['identifier'] = ID
                        logger.warning('sourceResource.identifier: {0} - {1}'.format('Not a PURL',
                                                                                     oai_id))
                is_shown_at = sourceResource['identifier']

            except (TypeError, UnboundLocalError) as err:
                logger.error(
                    'sourceResource.identifier: {0} - {1}'.format(err,
                                                                  oai_id))
                continue

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
            if record.metadata.get_element('.//{0}coverage'.format(dc)):
                sourceResource['spatial'] = [{'name': place}
                                             for place in
                                             record.metadata.get_element(
                                                 './/{0}coverage'.format(dc))]

            # sourceResource.publisher
            if record.metadata.get_element('.//{0}publisher'.format(dc)):
                sourceResource['publisher'] = record.metadata.get_element(
                    './/{0}publisher'.format(dc))

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rights = record.metadata.get_element('.//{0}rights'.format(dc))
            if rights:
                sourceResource['rights'] = [{'text': rights[0]}]
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
                        sourceResource['subject'].append({"name": term.strip(" ")})

            # sourceResource.title
            title = record.metadata.get_element('.//{0}title'.format(dc))
            if title:
                sourceResource['title'] = title
            else:
                logger.error('No sourceResource.rights - {0}'.format(oai_id))
                continue

            # sourceResource.type
            if record.metadata.get_element('.//{0}type'.format(dc)):
                sourceResource['type'] = record.metadata.get_element(
                    './/{0}type'.format(dc), delimiter=';')

            # webResource.fileFormat

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            try:
                preview = assets.thumbnail_service(record, tn)
            except (TypeError, UnboundLocalError) as err:
                logger.warning('aggregation.preview: {0} - {1}'.format(err, oai_id))
                pass

            # aggregation.provider

            # build record
            try:
                if is_shown_at:
                    doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)

                docs.append(doc)
            except UnboundLocalError:
                logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                continue

    return docs


def FlaLD_QDC(file_in, tn, dprovide, iprovide=None):
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

            # skip record handling
            try:
                if 'noharvest' in record.metadata.get_element('.//{0}requires'.format(dcterms)):
                    continue
            except TypeError:
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

            # sourceResource.contributor
            if record.metadata.get_element('.//{0}contributor'.format(dc)):
                sourceResource['contributor'] = [{"name": name}
                                                 for name in record.metadata.get_element(
                                                    './/{0}contributor'.format(dc), delimiter=';')]

            # sourceResource.creator
            if record.metadata.get_element('.//{0}creator'.format(dc)):
                sourceResource['creator'] = [{"name": name}
                                                 for name in record.metadata.get_element(
                                                    './/{0}creator'.format(dc), delimiter=';')]

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

            # sourceResource.genre
            if record.metadata.get_element('.//{0}format'.format(dc)):
                sourceResource['genre'] = []
                for element in record.metadata.get_element('.//{0}format'.format(dc),
                                                           delimiter=';'):
                    if element.lower() in IANA_type_list:
                        file_format = element.lower()
                        pass
                    elif len(element) > 0:
                        sourceResource['genre'].append({'name': element.strip(' ')})
                if len(sourceResource['genre']) == 0:
                    del sourceResource['genre']

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
                sourceResource['spatial'] = [{'name': place}
                                             for place in record.metadata.get_element(
                    './/{0}spatial'.format(dcterms), delimiter=';')]

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
                for rights_statement in record.metadata.get_element(
                        './/{0}rights'.format(dc)):
                    URI = rightsURI.search(rights_statement)
                    if URI:
                        URI_match = URI.string.split(" ")[-1]
                        sourceResource['rights'] = [{"@id": URI_match}]
                    else:
                        sourceResource['rights'] = [{"text": rights_statement}]

            else:
                logger.error('No sourceResource.rights - {0}'.format(oai_id))
                continue

            # sourceResource.subject
            if record.metadata.get_element('.//{0}subject'.format(dc)):
                sourceResource['subject'] = [{"name": name }
                                             for name in record.metadata.get_element(
                                             './/{0}subject'.format(dc), delimiter=';')]

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

            # build record
            try:
                if is_shown_at:
                    doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)

                docs.append(doc)
            except UnboundLocalError:
                logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                continue

    return docs


def FlaLD_MODS(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        records = OAIReader(data_in)
        docs = []
        for record in records:

            # deleted record handling for repox
            try:
                if 'deleted' in record.attrib.keys():
                    if record.attrib['deleted'] == 'true':
                        pass
            except AttributeError:
                pass

            # deleted record handling for OAI-PMH
            try:
                if 'status' in record.find('./{*}header').attrib.keys():
                    if record.find('./{*}header').attrib['status'] == 'deleted':
                        pass
            except AttributeError:
                pass

            if VERBOSE:
                print(record.oai_urn)
            logger.debug(record.oai_urn)
            sourceResource = {}

            if record.metadata is None:
                continue

            # sourceResource.alternative
            if len(record.metadata.titles) > 1:
                sourceResource['alternative'] = []
                if len(record.metadata.titles[1:]) >= 1:
                    for alternative_title in record.metadata.titles[1:]:
                        sourceResource['alternative'].append(alternative_title)

            # sourceResource.collection
            if record.metadata.collection:
                collection = record.metadata.collection
                sourceResource['collection'] = {}
                if collection.title:
                    sourceResource['collection']['name'] = collection.title
                if collection.location:
                    sourceResource['collection']['host'] = collection.location
                if collection.url:
                    sourceResource['collection']['_:id'] = collection.url

            # sourceResource.contributor
            try:

                for name in  record.metadata.names:
                    if name.role.text != 'Creator' or name.role.code != 'cre':
                        sourceResource['contributor'] = [{"@id": name.uri, "name": name.text}
                                                         if name.uri else
                                                         {"name": name.text}]
            except KeyError as err:
                logger.error('sourceResource.contributor: {0}, {1}'.format(err, record.oai_urn))
                pass

            # sourceResource.creator
            if record.metadata.get_creators:
                sourceResource['creator'] = [{"@id": name.uri, "name": name.text}
                                             if name.uri else
                                             {"name": name.text}
                                             for name in record.metadata.get_creators]

            # sourceResource.date
            if record.metadata.dates:
                date = record.metadata.dates[0].text
                if ' - ' in date:
                    sourceResource['date'] = {"displayDate": date,
                                              "begin": date[0:4],
                                              "end": date[-4:]}
                else:
                    sourceResource['date'] = {"displayDate": date,
                                              "begin": date,
                                              "end": date}

            # sourceResource.description
            if record.metadata.abstract:
                sourceResource['description'] = [abstract.text
                                                 for abstract in record.metadata.abstract]

            # sourceResource.extent
            if record.metadata.extent:
                sourceResource['extent'] = record.metadata.extent

            # sourceResource.format
            if record.metadata.form:
                sourceResource['format'] = record.metadata.form

            # sourceResource.genre
            if record.metadata.genre:
                sourceResource['genre'] = [{'name': genre.text,
                                            '@id': genre.uri}
                                           if genre.uri else
                                           {'name': genre.text}
                                           for genre in record.metadata.genre]

            # sourceResource.identifier
            try:
                sourceResource['identifier'] = record.metadata.purl[0]
            except IndexError as err:
                logger.error('sourceResource.identifier: {0}, {1}'.format(err, record.oai_urn))
                continue

            # sourceResource.language
            try:
                if record.metadata.language:
                    sourceResource['language'] = [{"name": lang.text,
                                                   "iso_639_3": lang.code}
                                                   for lang in record.metadata.language]
            except AttributeError as err:
                logger.error('sourceResource.language: {0}, {1}'.format(err, record.oai_urn))
                pass

            # sourceResource.place : sourceResource['spatial']
            try:
                if record.metadata.geographic_code and len(record.metadata.geographic_code) > 0:
                    sourceResource['spatial'] = []
                    for geo_code in record.metadata.geographic_code:
                        code, lat, long, label = assets.tgn_cache(geo_code)
                        sourceResource['spatial'].append({"lat": lat,
                                                          "long": long,
                                                          "name": label,
                                                          "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License."})
            except TypeError as err:
                logger.error('sourceResource.spatial: {0}, {1}'.format(err, record.oai_urn))
                continue
            
            # sourceResource.publisher
            if record.metadata.publisher:
                sourceResource['publisher'] = record.metadata.publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            if record.metadata.rights:
                sourceResource['rights'] = [{"@id": rights.uri}
                                            if rights.uri else
                                            {"text": rights.text}
                                            for rights in record.metadata.rights]
            else:
                logger.error('No sourceResource.rights - {0}'.format(record.oai_urn))
                continue

            # sourceResource.subject
            try:

                if record.metadata.subjects:
                    sourceResource['subject'] = [
                        {"@id": subject.uri, "name": subject.text}
                        if subject.uri is not None
                        else {"name": subject.text}
                        for subject in record.metadata.subjects]
            except (TypeError, IndexError) as err:
                logger.error('sourceResource.subject: {0}, {1}'.format(err, record.oai_urn))
                pass

            # sourceResource.title
            if record.metadata.titles:
                sourceResource['title'] = ['{}'.format(record.metadata.titles[0])]
            else:
                logger.error('No sourceResource.title: {0}'.format(record.oai_urn))
                continue

            # sourceResource.type
            sourceResource['type'] = record.metadata.type_of_resource

            # aggregation.dataProvider
            first_baptist = re.compile('^FSU_FBCTLH')
            leon_high = re.compile('^FSU_LeonHigh')
            fist_baptist_iid = first_baptist.search(record.metadata.iid)
            leon_high_iid = leon_high.search(record.metadata.iid)
            if fist_baptist_iid:
                data_provider = 'First Baptist Church of Tallahassee'
            elif leon_high_iid:
                data_provider = 'Leon High School, Tallahassee, Florida'
            else:
                data_provider = dprovide

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            pid = record.metadata.pid
            if pid is None:
                pid = record.oai_urn.split(':')[-1].replace('_',':')
            preview = assets.thumbnail_service(pid, tn)

            # aggregation.provider

            # build record
            try:
                if record.metadata.purl[0]:
                    doc = assets.build(record.oai_urn, sourceResource, data_provider, record.metadata.purl[0],
                                       preview, iprovide)

                docs.append(doc)
            except UnboundLocalError:
                logger.error('No aggregation.isShownAt - {0}'.format(record.oai_urn))
                continue

    return docs


def FlaLD_BepressDC(file_in, tn, dprovide, iprovide=None):
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
            if record.metadata.get_element('.//{0}source'.format(dc)):
                sourceResource['collection'] = {'name': record.metadata.get_element('.//{0}source'.format(dc))[0]}

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
            date = record.metadata.get_element('.//{0}date.created'.format(dc))
            if date:
                sourceResource['date'] = {"begin": date[0], "end": date[0], "displayDate": date[0]}

            # sourceResource.description
            if record.metadata.get_element('.//{0}description.abstract'.format(dc)):
                sourceResource['description'] = record.metadata.get_element(
                    './/{0}description.abstract'.format(dc), delimiter=';')

            # sourceResource.extent

            # sourceResource.format
            if record.metadata.get_element('.//{0}format'.format(dc)):
                sourceResource['format'] = record.metadata.get_element(
                    './/{0}format'.format(dc))

            # sourceResource.genre

            # sourceResource.identifier
            for identifier in record.metadata.get_element('.//{0}identifier'.format(dc)):
                if 'http' in identifier:
                    is_shown_at = identifier
            sourceResource['identifier'] = oai_id

            # sourceResource.language
            if record.metadata.get_element('.//{0}language'.format(dc)):
                sourceResource['language'] = []
                for lang in record.metadata.get_element('.//{0}language'.format(dc), delimiter=';'):
                    results = assets.iso639_2code(lang.split('-')[0])
                    sourceResource['language'].append(results)

            # sourceResource.place : sourceResource['spatial']
            if record.metadata.get_element('.//{0}coverage'.format(dc)):
                sourceResource['spatial'] = [{'name': place}
                                             for place in
                                             record.metadata.get_element(
                                                 './/{0}coverage'.format(dc))]

            # sourceResource.publisher
            if record.metadata.get_element('.//{0}publisher'.format(dc)):
                sourceResource['publisher'] = record.metadata.get_element(
                    './/{0}publisher'.format(dc))

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            rightsURI = re.compile('http://rightsstatements')
            if record.metadata.get_element('.//{0}rights'.format(dc)):
                for rights_statement in record.metadata.get_element(
                        './/{0}rights'.format(dc)):
                    URI = rightsURI.search(rights_statement)
                    if URI:
                        URI_match = URI.string.split(" ")[-1]
                        sourceResource['rights'] = [{"@id": URI_match}]
                    else:
                        sourceResource['rights'] = [{"text": rights_statement}]

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

            # sourceResource.title
            title = record.metadata.get_element('.//{0}title'.format(dc))
            if title:
                sourceResource['title'] = title
            else:
                logger.error('No sourceResource.rights - {0}'.format(oai_id))
                continue

            # sourceResource.temporal
            temporal = record.metadata.get_element('.//{0}coverage'.format(dc))
            if temporal:
                sourceResource['temporal'] = temporal

            # sourceResource.type
            if record.metadata.get_element('.//{0}type'.format(dc)):
                if 'type' in sourceResource.keys():
                    sourceResource['type'] = sourceResource['type'] + record.metadata.get_element(
                        './/{0}type'.format(dc))
                else:
                    sourceResource['type'] = record.metadata.get_element(
                        './/{0}type'.format(dc), delimiter=';')
            if record.metadata.get_element('.//{0}format'.format(dc)):
                if 'type' in sourceResource.keys():
                    sourceResource['type'] = sourceResource['type'] + record.metadata.get_element(
                        './/{0}format'.format(dc))
                else:
                    sourceResource['type'] = record.metadata.get_element(
                        './/{0}format'.format(dc), delimiter=';')


            # webResource.fileFormat

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvide

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            if record.metadata.get_element('.//{0}description'.format(dc)):
                preview = record.metadata.get_element('.//{0}description'.format(dc))[0]

            # aggregation.provider

            # build record
            try:
                if is_shown_at:
                    doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)

                docs.append(doc)
            except UnboundLocalError:
                logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                continue

    return docs
