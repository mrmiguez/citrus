import re

import dateparser
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


def SSDN_QDC(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        logger = assets.CSVLogger('SSDN_QDC', provider=dprovide)
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
            rights_uri = re.compile('^http[s]*://rightsstatements')
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

            # build record
            try:
                if is_shown_at:
                    doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)

                docs.append(doc)
            except UnboundLocalError:
                logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                continue

    return docs


def SSDN_DC(file_in, tn, dprovide, iprovide=None):
    def clean_mark_up(text):
        mark_up_re = re.compile('<.*?>')
        new_line_re = re.compile('\n')
        clean_text = re.sub(mark_up_re, '', text)
        clean_text = re.sub(new_line_re, ' ', clean_text)
        return clean_text

    with open(file_in, encoding='utf-8') as data_in:
        logger = assets.CSVLogger('SSDN_DC', provider=dprovide)
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
                try:
                    d = dateparser.parse(date[0], languages=['en']).date().isoformat()
                    sourceResource['date'] = {"begin": d, "end": d, "displayDate": d}
                except AttributeError as err:
                    logger.warning('sourceResource.date: {0}, {1}'.format(err, record.oai_urn))
                    sourceResource['date'] = date[0]

            # sourceResource.description
            if record.metadata.get_element('.//{0}description'.format(dc)):
                sourceResource['description'] = [clean_mark_up(desc) for desc in record.metadata.get_element(
                    './/{0}description'.format(dc), delimiter=';')]

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
            rights_uri = re.compile('^http[s]*://rightsstatements')
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
            try:
                for identifier in record.metadata.get_element('.//{0}identifier'.format(dc)):
                    if 'http' in identifier:
                        is_shown_at = identifier
            except (TypeError, UnboundLocalError) as err:
                logger.warning('aggregation.isShownAt: {0} - {1}'.format(err, oai_id))
                pass

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
            except (NameError, UnboundLocalError):
                logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                continue

    return docs


def SSDN_OMEKA_DC(file_in, tn, dprovide, iprovide=None):
    def clean_mark_up(text):
        mark_up_re = re.compile('<.*?>')
        new_line_re = re.compile('\n')
        clean_text = re.sub(mark_up_re, '', text)
        clean_text = re.sub(new_line_re, ' ', clean_text)
        return clean_text

    with open(file_in, encoding='utf-8') as data_in:
        logger = assets.CSVLogger('SSDN_DC', provider=dprovide)
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
                try:
                    d = dateparser.parse(date[0], languages=['en']).date().isoformat()
                    sourceResource['date'] = {"begin": d, "end": d, "displayDate": d}
                except AttributeError as err:
                    logger.warning('sourceResource.date: {0}, {1}'.format(err, record.oai_urn))
                    sourceResource['date'] = date[0]

            # sourceResource.description
            if record.metadata.get_element('.//{0}description'.format(dc)):
                sourceResource['description'] = [clean_mark_up(desc) for desc in record.metadata.get_element(
                    './/{0}description'.format(dc), delimiter=';')]

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
            rights_uri = re.compile('^http[s]*://rightsstatements')
            if record.metadata.get_element('.//{0}rights'.format(dc)):
                for rights_statement in record.metadata.get_element(
                        './/{0}rights'.format(dc)):
                    uri = rights_uri.search(clean_mark_up(rights_statement)[
                                            clean_mark_up(rights_statement).rfind('http://rightsstatements.org'):-1])
                    if uri:
                        sourceResource['rights'] = [{"@id": uri.string.strip()}]
                        break
                    else:
                        sourceResource['rights'] = [{"text": clean_mark_up(rights_statement).strip()}]

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
            try:
                for identifier in record.metadata.get_element('.//{0}identifier'.format(dc)):
                    if 'omeka.net/' in identifier:
                        is_shown_at = identifier
            except (TypeError, UnboundLocalError) as err:
                logger.warning('aggregation.isShownAt: {0} - {1}'.format(err, oai_id))
                pass

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
            except (NameError, UnboundLocalError):
                logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                continue

    return docs


def SSDN_MODS(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        logger = assets.CSVLogger('SSDN_MODS', provider=dprovide)
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
            try:
                if len(record.metadata.titles) > 1:
                    sourceResource['alternative'] = []
                    if len(record.metadata.titles[1:]) >= 1:
                        for alternative_title in record.metadata.titles[1:]:
                            sourceResource['alternative'].append(alternative_title)
            except AttributeError:
                print(record.oai_urn)

            # sourceResource.collection

            # sourceResource.contributor
            try:

                for name in record.metadata.names:
                    if name.role.text != 'Creator' and name.role.code != 'cre' and name.role.text is not None and name.role.code is not None:
                        sourceResource['contributor'] = [{"@id": name.uri, "name": name.text}
                                                         if name.uri else
                                                         {"name": name.text}]
            except KeyError as err:
                logger.error('sourceResource.contributor: {0}, {1}'.format(err, record.oai_urn))
                pass

            # sourceResource.creator
            name_list = []
            if record.metadata.get_creators:
                for name in record.metadata.get_creators:
                    name_list.append(name)
            if record.metadata.names:
                for name in record.metadata.names:
                    if name.role.text is None or name.role.code is None:
                        name_list.append(name)
            sourceResource['creator'] = [{"@id": name.uri, "name": name.text}
                                         if name.uri else
                                         {"name": name.text}
                                         for name in name_list]

            # sourceResource.date
            try:
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
            except (TypeError, UnboundLocalError) as err:
                logger.warning('sourceResource.date: {0}'.format(err))
                pass

            # sourceResource.description
            if record.metadata.abstract:
                sourceResource['description'] = [abstract.text
                                                 for abstract in record.metadata.abstract]
            try:
                for toc in record.metadata.iterfind('.//{http://www.loc.gov/mods/v3}tableOfContents'):
                    sourceResource['description'].append(toc.text)
            except KeyError:
                sourceResource['description'] = [toc.text for toc
                                                 in record.metadata.findall('.//{http://www.loc.gov/mods/v3}tableOfContents')]

            # sourceResource.extent
            if record.metadata.extent:
                sourceResource['extent'] = record.metadata.extent

            # sourceResource.format
            if record.metadata.genre:
                sourceResource['format'] = [{'name': genre.text,
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
            for subject in record.metadata.subjects:
                for c in subject.elem.getchildren():
                    if 'eographic' in c.tag:
                        sourceResource['spatial'] = {"name": subject.text}

            # sourceResource.publisher
            if record.metadata.publisher:
                sourceResource['publisher'] = record.metadata.publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            if record.metadata.rights:
                sourceResource['rights'] = [{"@id": rights.text}
                                            if "http://rightsstatements.org" in rights.text else
                                            {"text": rights.text}
                                            for rights in record.metadata.rights[:2]]
                                            # slicing isn't ideal here since it depends on element order
            else:
                logger.error('No sourceResource.rights - {0}'.format(record.oai_urn))
                continue

            # sourceResource.subject
            try:

                if record.metadata.subjects:
                    sourceResource['subject'] = []
                    for subject in record.metadata.subjects:
                        for child in subject.elem:
                            if 'eographic' not in child.tag:
                                sourceResource['subject'].append({"name": subject.text})
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
            data_provider = dprovide

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            pid = record.metadata.pid
            if pid is None:
                pid = record.oai_urn.split(':')[-1].replace('_', ':')
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
