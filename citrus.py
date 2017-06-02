import re
import logging
import requests
from pymods import OAIReader
from bs4 import BeautifulSoup

# custom functions and variables
import assets
from citrus_config import PROVIDER


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


def FlaLD_QDC(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
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
                if date is not None:
                    sourceResource['date'] = {"begin": date[0], "end": date[0]}

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
                if len(description) > 1:
                    sourceResource['description'] = []
                    for item in description:
                        sourceResource['description'].append(item)
                elif len(description) == 1:
                    sourceResource['description'] = description[0]

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
                    for element in record.metadata.get_element(
                            './/{0}language'.format(dc), delimiter=';'):
                        if len(element) > 3:
                            sourceResource['language'] = {"name": element}
                        else:
                            sourceResource['language'] = {"iso_639_3": element}

                # sourceResource.place : sourceResource['spatial']
                if record.metadata.get_element('.//{0}spatial'.format(dcterms)):
                    sourceResource['spatial'] = record.metadata.get_element(
                        './/{0}spatial'.format(dcterms), delimiter=';')

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
                        for rights_statement in record.metadata.get_element(
                                './/{0}rights'.format(dc)):
                            URI = rightsURI.search(rights_statement)
                            if URI:
                                URI_match = URI.string.split(" ")[-1]
                            else:
                                rights_text = rights_statement
                        sourceResource['rights'] = {"@id": URI_match, "text": rights_text}
                    else:
                        sourceResource['rights'] = record.metadata.get_element(
                            './/{0}rights'.format(dc))

                else:
                    logging.warning('No sourceResource.rights - {0}'.format(oai_id))
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
                    logging.warning('No sourceResource.title - {0}'.format(oai_id))
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
                for identifier in local_id:
                    if 'http' in identifier:
                        is_shown_at = identifier
                        preview = assets.thumbnail_service(identifier, tn)

                # aggregation.provider

                docs.append({"@context": "http://api.dp.la/items/context",
                             "sourceResource": sourceResource,
                             "aggregatedCHO": "#sourceResource",
                             "dataProvider": data_provider,
                             "isShownAt": is_shown_at,
                             "preview": preview,
                             "provider": PROVIDER})
    return docs


def FlaLD_DC(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
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

                # sourceResource.collection

                # sourceResource.contributor
                if record.metadata.get_element('.//{0}contributor'.format(dc)):
                    sourceResource['contributor'] = [{"name": name}
                                                     for name in record.metadata.get_element(
                                                        './/{0}contributor'.format(dc), delimiter=';')]

                # sourceResource.creator
                if record.metadata.get_element('.//{0}creator'.format(dc)):
                    sourceResource['creator'] = []
                    for name in record.metadata.get_element('.//{0}creator'.format(dc), delimiter=';'):
                        # need to test for ( Contributor ) and ( contributor )
                        if (len(name) > 0) and ("ontributor )" not in name):
                            sourceResource['creator'].append({"name": name.strip(" ") })
                        elif "ontributor )" in name:
                            if 'contributor' not in sourceResource.keys():
                                sourceResource['contributor'] = []
                                sourceResource['contributor'].append({"name": name.strip(" ").rstrip("( Contributor )").rstrip("( contributor )")})
                            else:
                                sourceResource['contributor'].append(
                                    {"name": name.strip(" ").rstrip("( Contributor )").rstrip("( contributor )")})

                # sourceResource.date
                date = record.metadata.get_element('.//{0}date'.format(dc))
                if date:
                    sourceResource['date'] = { "begin": date[0], "end": date[0] }

                # sourceResource.description
                if record.metadata.get_element('.//{0}description'.format(dc)):
                    sourceResource['description'] = record.metadata.get_element('.//{0}description'.format(dc), delimiter=';')
                #     for item in record.metadata.get_element('.//{0}description'.format(dc)):
                #         description.append(item)
                # if len(description) > 1:
                #     sourceResource['description'] = []
                #     for item in description:
                #         sourceResource['description'].append(item)
                # elif len(description) == 1:
                #     sourceResource['description'] = description[0]

                # sourceResource.extent

                # sourceResource.format
                if record.metadata.get_element('.//{0}format'.format(dc)):
                    sourceResource['format'] = record.metadata.get_element('.//{0}format'.format(dc))

                # sourceResource.genre

                # sourceResource.identifier
                dPantherPURL = re.compile('dpService/dpPurlService/purl')
                identifier = record.metadata.get_element('.//{0}identifier'.format(dc))
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
                            logging.warning('sourceResource.identifier: {0} - {1}\n'.format(err, oai_id))
                            pass
                else:
                    sourceResource['identifier'] = identifier

                # sourceResource.language
                if record.metadata.get_element('.//{0}language'.format(dc)):
                    sourceResource['language'] = []
                    for element in record.metadata.get_element(
                            './/{0}language'.format(dc), delimiter=';'):
                        if len(element) > 3:
                            sourceResource['language'] = {"name": element}
                        else:
                            sourceResource['language'] = {"iso_639_3": element}

                # sourceResource.place : sourceResource['spatial']
                if record.metadata.get_element('.//{0}coverage'.format(dc)):
                    sourceResource['spatial'] = record.metadata.get_element('.//{0}coverage'.format(dc))

                # sourceResource.publisher
                if record.metadata.get_element('.//{0}publisher'.format(dc)):
                    sourceResource['publisher'] = record.metadata.get_element('.//{0}publisher'.format(dc))

                # sourceResource.relation

                # sourceResource.isReplacedBy

                # sourceResource.replaces

                # sourceResource.rights
                rights = record.metadata.get_element('.//{0}rights'.format(dc))
                if rights:
                    sourceResource['rights'] = rights
                else:
                    logging.warning('No sourceResource.rights - {0}'.format(oai_id))
                    continue

                # sourceResource.subject
                if record.metadata.get_element('.//{0}subject'.format(dc)):
                    sourceResource['subject'] = []
                    for term in record.metadata.get_element('.//{0}subject'.format(dc), delimiter=';'):
                        term = re.sub("\( lcsh \)$", '', term)
                        if len(term) > 0:
                            sourceResource['subject'].append({"name": term.strip(" ") })

                # sourceResource.title
                title = record.metadata.get_element('.//{0}title'.format(dc))
                if title:
                    sourceResource['title'] = title
                else:
                    logging.warning('No sourceResource.rights - {0}'.format(oai_id))
                    continue

                # sourceResource.type
                if record.metadata.get_element('.//{0}type'.format(dc)):
                    sourceResource['type'] = record.metadata.get_element('.//{0}type'.format(dc), delimiter=';')
                    # for element in OAI_QDC.split_lookup(record, './/{0}type'.format(dc)):
                    #     for term in element:
                    #         if len(term) > 0:
                    #             sourceResource['type'].append(term.strip(" "))

                # webResource.fileFormat

                # aggregation.dataProvider
                data_provider = dprovide

                # aggregation.intermediateProvider

                # aggregation.isShownAt

                # aggregation.preview
                try:
                    preview = assets.thumbnail_service(PURL_match, tn)
                except UnboundLocalError as err:
                    logging.warning('aggregation.preview: {0} - {1}\n'.format(err, oai_id))
                    continue

                # aggregation.provider

                try:
                    docs.append({"@context": "http://api.dp.la/items/context",
                                 "sourceResource": sourceResource,
                                 "aggregatedCHO": "#sourceResource",
                                 "dataProvider": data_provider,
                                 "isShownAt": PURL_match,
                                 "preview": preview,
                                 "provider": PROVIDER})
                except NameError as err:
                    logging.warning('aggregation.preview: {0} - {1}\n'.format(err, oai_id))
                    pass

    return docs


def FlaLD_MODS(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        records = OAIReader(data_in)
        docs = []
        for record in records:

            sourceResource = {}

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
                logging.warning('sourceResource.contributor: {0}, {1}\n'.format(err, record.oai_urn))
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
                sourceResource['identifier'] = {"@id": record.metadata.purl[0],
                                                "text": record.metadata.iid}
            except IndexError as err:
                logging.warning('sourceResource.identifier: {0}, {1}\n'.format(err, record.oai_urn))
                continue

            # sourceResource.language
            if record.metadata.language:
                sourceResource['language'] = [{"name": lang.text,
                                               "iso_639_3": lang.code}
                                               for lang in record.metadata.language]

            # sourceResource.place : sourceResource['spatial']
            if record.metadata.geographic_code:
                sourceResource['spatial'] = []
                for geo_code in record.metadata.geographic_code:
                    code, lat, long, label = assets.tgn_cache(geo_code)
                    sourceResource['spatial'].append({"lat": lat,
                                                      "long": long,
                                                      "name": label,
                                                      "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License."})

            # sourceResource.publisher
            if record.metadata.publisher:
                sourceResource['publisher'] = record.metadata.publisher

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            if record.metadata.rights:
                sourceResource['rights'] = [{"@id": rights.uri, "text": rights.text}
                                            if rights.uri else
                                            {"text": rights.text}
                                            for rights in record.metadata.rights]
            else:
                logging.warning('No sourceResource.rights - {0}'.format(record.oai_urn))
                continue

            # sourceResource.subject
            try:

                if record.metadata.subjects:
                    sourceResource['subject'] = [
                        {"@id": subject.uri, "name": subject.text}
                        if subject.uri is not None
                        else {"name": subject.text}
                        for subject in record.metadata.subjects]
            except TypeError as err:
                logging.warning('sourceResource.subject: {0}, {1}\n'.format(err, record.oai_urn))
                pass

            # sourceResource.title
            if record.metadata.titles:
                sourceResource['title'] = record.metadata.titles[0]
            else:
                logging.warning('No sourceResource.title: {0}'.format(record.oai_urn))
                continue

            # sourceResource.type
            sourceResource['type'] = record.metadata.type_of_resource

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvider  # TODO
            if iprovide:
                pass
            else:
                pass

            # aggregation.isShownAt

            # aggregation.preview
            pid = record.metadata.pid
            preview = assets.thumbnail_service(pid, tn)

            # aggregation.provider

            docs.append({"@context": "http://api.dp.la/items/context",
                         "sourceResource": sourceResource,
                         "aggregatedCHO": "#sourceResource",
                         "dataProvider": data_provider,
                         "isShownAt": record.metadata.purl[0],
                         "preview": preview,
                         "provider": PROVIDER})
        return docs
