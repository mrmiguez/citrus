import re
import json
import logging
import requests
from lxml import etree
from bs4 import BeautifulSoup
from pymods import MODSReader

# custom functions and variables
import assets
from master_config import PROVIDER

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
                record_list.append(oai_record)
            self.nsroot = 'oai_dc'
            self.set_spec = self.root.find('.//{0}setSpec'.format(nameSpace_default['oai_dc'])).text
            oai_id = self.root.find('.//{0}header/{0}identifier'.format(nameSpace_default['oai_dc'])).text
            oai_urn = ""
            for part in oai_id.split(':')[:-1]:
                oai_urn = oai_urn + ':' + part
            self.oai_urn = oai_urn.strip(':')

        elif 'repox' in self.nsmap:
            for oai_record in self.root.iterfind('.//{0}record'.format(nameSpace_default['repox'])):
                record_list.append(oai_record)
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


def FlaLD_QDC(file_in, tn, dprovide, iprovide=None):
    with open(file_in, encoding='utf-8') as data_in:
        records = OAI_QDC(data_in)
        docs = []
        for record in records.record_list:

            if 'deleted' in record.attrib.keys():
                if record.attrib['deleted'] == 'true':
                    pass

            else:
                oai_id = record.attrib['id']

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
                    sourceResource['date'] = { "begin": date[0], "end": date[0] }

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
                else:
                    logging.warning('No sourceResource.rights - {0}'.format(oai_id))
                    continue
                    
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
                else:
                    logging.warning('No sourceResource.title - {0}'.format(oai_id))
                    continue

                # sourceResource.type
                if OAI_QDC.simple_lookup(record, './/{0}type'.format(nameSpace_default['dc'])) is not None:
                    sourceResource['type'] = []
                    for element in OAI_QDC.split_lookup(record, './/{0}type'.format(nameSpace_default['dc'])):
                        for term in element:
                            if len(term) > 0:
                                sourceResource['type'].append(term.strip(" "))

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
        records = OAI_QDC(data_in)
        docs = []
        for record in records.record_list:

            if 'deleted' in record.attrib.keys():
                if record.attrib['deleted'] == 'true':
                    pass

            else:
                oai_id = record.attrib['id']

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
                    sourceResource['date'] = { "begin": date[0], "end": date[0] }

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
                            logging.warning('sourceResource.identifier: {0} - {1}\n'.format(err, oai_id))
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
                else:
                    logging.warning('No sourceResource.rights - {0}'.format(oai_id))
                    continue

                # sourceResource.subject
                if OAI_QDC.simple_lookup(record, './/{0}subject'.format(nameSpace_default['dc'])) is not None:
                    sourceResource['subject'] = []
                    for element in OAI_QDC.split_lookup(record, './/{0}subject'.format(nameSpace_default['dc'])):
                        for term in element:
                            term = re.sub("\( lcsh \)$", '', term)
                            if len(term) > 0:
                                sourceResource['subject'].append({"name": term.strip(" ") })

                # sourceResource.title
                title = OAI_QDC.simple_lookup(record, './/{0}title'.format(nameSpace_default['dc']))
                if title is not None:
                    sourceResource['title'] = title
                else:
                    logging.warning('No sourceResource.rights - {0}'.format(oai_id))
                    continue

                # sourceResource.type
                if OAI_QDC.simple_lookup(record, './/{0}type'.format(nameSpace_default['dc'])) is not None:
                    sourceResource['type'] = []
                    for element in OAI_QDC.split_lookup(record, './/{0}type'.format(nameSpace_default['dc'])):
                        for term in element:
                            if len(term) > 0:
                                sourceResource['type'].append(term.strip(" "))

                # webResource.fileFormat

                # aggregation.dataProvider
                data_provider = dprovide

                # aggregation.intermediateProvider

                # aggregation.isShownAt

                # aggregation.preview
                preview = assets.thumbnail_service(PURL_match, tn)

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
        records = MODSReader(data_in)
        docs = []
        for record in records:

            sourceResource = {}

            # sourceResource.alternative
            if record.title_constructor() is not None and record.title_constructor()[1:] is not None:
                sourceResource['alternative'] = []
                if len(record.title_constructor()[1:]) >= 1:
                    for alternative_title in record.title_constructor()[1:]:
                        sourceResource['alternative'].append(alternative_title)

            # sourceResource.collection
            if record.collection() is not None:
                collection = record.collection()
                sourceResource['collection'] = {}
                if 'title' in collection.keys():
                    sourceResource['collection']['name'] = collection['title']
                if 'location' in collection.keys():
                    sourceResource['collection']['host'] = collection['location']
                if 'url' in collection.keys():
                    sourceResource['collection']['_:id'] = collection['url']

            # sourceResource.contributor
            try:

                if record.name_constructor() is not None:
                    sourceResource['contributor'] = []
                    for name in record.name_constructor():

                        if any(key in name.keys() for key in ['roleText', 'roleCode']) is False:
                            if 'valueURI' in name.keys():
                                sourceResource['contributor'].append({"@id": name['valueURI'],
                                                                      "name": name['text']} )
                            else:
                                sourceResource['contributor'].append({"name": name['text']} )

                        elif 'roleText' in name.keys():
                            if name['roleText'].lower() != 'creator':
                                if 'valueURI' in name.keys():
                                    sourceResource['contributor'].append({ "@id": name['valueURI'],
                                                                       "name": name['text'] })
                                else:
                                    sourceResource['contributor'].append({ "name": name['text'] })
                        elif 'roleCode' in name.keys():
                            if name['roleCode'].lower() != 'cre':
                                if 'valueURI' in name.keys():
                                    sourceResource['contributor'].append({ "@id": name['valueURI'],
                                                                       "name": name['text'] })
                                else:
                                    sourceResource['contributor'].append({ "name": name['text'] })

                        else:
                            pass

                    if len(sourceResource['contributor']) < 1:
                        del sourceResource['contributor']

            except KeyError as err:
                logging.warning('sourceResource.contributor: {0}, {1}\n'.format(err, record.pid_search()))
                pass

            if record.name_constructor() is not None:
                sourceResource['creator'] = []
                for name in record.name_constructor():

                    if 'roleText' in name.keys():
                        if name['roleText'].lower() == 'creator':
                            if 'valueURI' in name.keys():
                                sourceResource['creator'].append({ "@id": name['valueURI'],
                                                                   "name": name['text'] })
                            else:
                                sourceResource['creator'].append({ "name": name['text'] })
                    elif 'roleCode' in name.keys():
                        if name['roleCode'].lower() == 'cre':
                            if 'valueURI' in name.keys():
                                sourceResource['creator'].append({ "@id": name['valueURI'],
                                                                   "name": name['text'] })
                            else:
                                sourceResource['creator'].append({ "name": name['text'] })
                    else:
                        pass

            # sourceResource.date
            if record.date_constructor() is not None:
                date = record.date_constructor()
                if ' - ' in date:
                    sourceResource['date'] = { "displayDate": date,
                                               "begin": date[0:4],
                                               "end": date[-4:] }
                else:
                    sourceResource['date'] = { "displayDate": date,
                                               "begin": date,
                                               "end": date }

            # sourceResource.description
            if record.abstract() is not None:
                if len(record.abstract()) > 1:
                    sourceResource['description'] = []
                    for description in record.abstract():
                        sourceResource['description'].append(description)
                else:
                    sourceResource['description'] = record.abstract()

            # sourceResource.extent
            if record.extent() is not None:
                if len(record.extent()) > 1:
                    sourceResource['extent'] = []
                    for extent in record.extent():
                        sourceResource['extent'].append(extent)
                else:
                    sourceResource['extent'] = record.extent()[0]

            # sourceResource.format
            if record.form() is not None:
                if len(record.form()) > 1:
                    sourceResource['format'] = []
                    for form in record.form():
                        sourceResource['format'].append(form)
                else:
                    sourceResource['format'] = record.form()[0]

            # sourceResource.genre
            if record.genre() is not None:
                if len(record.genre()) > 1:
                    sourceResource['genre'] = []
                    for genre in record.genre():
                        genre_elem = {}
                        for key, value in genre.items():
                            if 'term' == key:
                                genre_elem['name'] = value
                            elif 'valueURI' == key:
                                genre_elem['@id'] = value
                        sourceResource['genre'].append(genre_elem)
                else:
                    genre_elem = {}
                    for key, value in record.genre()[0].items():
                        if 'term' == key:
                            genre_elem['name'] = value
                        elif 'valueURI' == key:
                            genre_elem['@id'] = value
                    sourceResource['genre'] = genre_elem

            # sourceResource.identifier
            sourceResource['identifier'] = { "@id": record.purl_search(),
                                             "text": record.local_identifier() }

            # sourceResource.language
            if record.language() is not None:
                language_list = []
                for language in record.language():
                    if len(language) > 1:
                        language_dict = { "name": language['text'],
                                          "iso_639_3": language['code'] }
                    else:
                        if 'text' in language.keys():
                            language_dict = { "name": language['text'] }
                        else:
                            pass
                    language_list.append(language_dict)
                sourceResource['language'] = language_list

            # sourceResource.place : sourceResource['spatial']
            geo_code_list = record.geographic_code()
            if geo_code_list is not None:
                sourceResource['spatial'] = []
                for geo_code in geo_code_list:

                    code, lat, long, label = assets.tgn_cache(geo_code)
                    sourceResource['spatial'].append({"lat": lat,
                                                      "long": long,
                                                      "name": label,
                                                      "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License." })

                    #tgn_prefix = 'http://vocab.getty.edu/tgn/'

                    '''
                    # Implementation using the schema.org namespace
                    # tgn_geometry = geo_code + '-geometry.jsonld'
                    # geometry = requests.get(tgn_prefix + tgn_geometry)
                    # geometry_json = json.loads(geometry.text)
                    # lat = geometry_json['http://schema.org/latitude']['@value']
                    # long = geometry_json['http://schema.org/longitude']['@value']
                    '''

                    #tgn_place = geo_code + '-place.jsonld'
                    #place = requests.get(tgn_prefix + tgn_place)
                    #if place.status_code == 200:
                    #    place_json = json.loads(place.text)
                    #    lat = place_json['http://www.w3.org/2003/01/geo/wgs84_pos#lat']['@value']
                    #    long = place_json['http://www.w3.org/2003/01/geo/wgs84_pos#long']['@value']
                    #    sourceResource['spatial'].append({ "lat": lat,
                    #                                       "long": long,
                    #                                       "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License." })

            # sourceResource.publisher
            if record.publisher() is not None:
                if len(record.publisher()) > 1:
                    sourceResource['publisher'] = []
                    for publisher in record.publisher():
                        sourceResource['publisher'].append(publisher)
                else:
                    sourceResource['publisher'] = record.publisher()[0]

            # sourceResource.relation

            # sourceResource.isReplacedBy

            # sourceResource.replaces

            # sourceResource.rights
            if record.rights() is not None:
                if len(record.rights()) > 1:
                    sourceResource['rights'] = {"@id": record.rights()['URI'],
                                                "text": record.rights()['text']}
                else:
                    sourceResource['rights'] = record.rights()['text']
            else:
                logging.warning('No sourceResource.rights - {0}'.format(record.pid_search()))
                continue

            # sourceResource.subject
            try:

                if record.subject() is not None:
                    sourceResource['subject'] = []
                    for subject in record.subject():
                        non_alpha_char = re.compile("^[^a-zA-Z]+$")
                        if non_alpha_char.match(subject['text']) is None:

                            if 'valueURI' in subject.keys():
                                sourceResource['subject'].append({"@id": subject['valueURI'],
                                                                  "name": subject['text'] })
                            else:
                                sourceResource['subject'].append({"name": subject['text'] })
                        else:
                            pass

            except TypeError as err:
                logging.warning('sourceResource.subject: {0}, {1}\n'.format(err, record.pid_search()))
                pass

            # sourceResource.title
            if record.title_constructor() is not None:
                sourceResource['title'] = record.title_constructor()[0]
            else:
                logging.warning('No sourceResource.title: {0}'.format(record.pid_search()))
                continue

            # sourceResource.type
            sourceResource['type'] = record.type_of_resource()

            # aggregation.dataProvider
            data_provider = dprovide

            # aggregation.intermediateProvider #TODO

            # aggregation.isShownAt

            # aggregation.preview
            pid = record.pid_search()
            preview = assets.thumbnail_service(pid, tn)

            # aggregation.provider

            docs.append({"@context": "http://api.dp.la/items/context",
                         "sourceResource": sourceResource,
                         "aggregatedCHO": "#sourceResource",
                         "dataProvider": data_provider,
                         "isShownAt": record.purl_search(),
                         "preview": preview,
                         "provider": PROVIDER})
        return docs
