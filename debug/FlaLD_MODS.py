#!/usr/bin/env python3

import sys
import json
import requests
from pymods import OAIReader
from lxml import etree  # test

PROVIDER = 'FSU'
data_provider = 'FSU'

def write_json_ld(docs):
    with open('testData/fsu_digital_library-1.json', 'w') as jsonOutput:
        json.dump(docs, jsonOutput)


with open(sys.argv[1], encoding='utf-8') as data_in:
    records = OAIReader(data_in)
    docs = []
    for record in records:

        sourceResource = {}

        # sourceResource.alternative
        if record.metadata.titles[1:] is not None:
            sourceResource['alternative'] = []
            if len(record.metadata.titles[1:]) >= 1:
                for alternative_title in record.metadata.titles[1:]:
                    sourceResource['alternative'].append(alternative_title)

        # # sourceResource.collection
        # if record.collection() is not None:
        #     collection = record.collection()
        #     sourceResource['collection'] = {}
        #     if 'title' in collection.keys():
        #         sourceResource['collection']['name'] = collection['title']
        #     if 'location' in collection.keys():
        #         sourceResource['collection']['host'] = collection['location']
        #     if 'url' in collection.keys():
        #         sourceResource['collection']['_:id'] = collection['url']
        #
        # # sourceResource.contributor
        # try:
        #
        #     if record.name_constructor() is not None:
        #         sourceResource['contributor'] = []
        #         for name in record.name_constructor():
        #
        #             if any(key in name.keys() for key in ['roleText', 'roleCode']) is False:
        #                 if 'valueURI' in name.keys():
        #                     sourceResource['contributor'].append({"@id": name['valueURI'],
        #                                                           "name": name['text']})
        #                 else:
        #                     sourceResource['contributor'].append({"name": name['text']})
        #
        #             elif 'roleText' in name.keys():
        #                 if name['roleText'].lower() != 'creator':
        #                     if 'valueURI' in name.keys():
        #                         sourceResource['contributor'].append({"@id": name['valueURI'],
        #                                                               "name": name['text']})
        #                     else:
        #                         sourceResource['contributor'].append({"name": name['text']})
        #             elif 'roleCode' in name.keys():
        #                 if name['roleCode'].lower() != 'cre':
        #                     if 'valueURI' in name.keys():
        #                         sourceResource['contributor'].append({"@id": name['valueURI'],
        #                                                               "name": name['text']})
        #                     else:
        #                         sourceResource['contributor'].append({"name": name['text']})
        #
        #             else:
        #                 pass
        #
        #         if len(sourceResource['contributor']) < 1:
        #             del sourceResource['contributor']
        #
        # except KeyError as err:
        #     logging.warning('sourceResource.contributor: {0}, {1}\n'.format(err, record.pid_search()))
        #     pass
        #
        # if record.name_constructor() is not None:
        #     sourceResource['creator'] = []
        #     for name in record.name_constructor():
        #
        #         if 'roleText' in name.keys():
        #             if name['roleText'].lower() == 'creator':
        #                 if 'valueURI' in name.keys():
        #                     sourceResource['creator'].append({"@id": name['valueURI'],
        #                                                       "name": name['text']})
        #                 else:
        #                     sourceResource['creator'].append({"name": name['text']})
        #         elif 'roleCode' in name.keys():
        #             if name['roleCode'].lower() == 'cre':
        #                 if 'valueURI' in name.keys():
        #                     sourceResource['creator'].append({"@id": name['valueURI'],
        #                                                       "name": name['text']})
        #                 else:
        #                     sourceResource['creator'].append({"name": name['text']})
        #         else:
        #             pass
        #
        # # sourceResource.date
        # if record.date_constructor() is not None:
        #     date = record.date_constructor()
        #     if ' - ' in date:
        #         sourceResource['date'] = {"displayDate": date,
        #                                   "begin": date[0:4],
        #                                   "end": date[-4:]}
        #     else:
        #         sourceResource['date'] = {"displayDate": date,
        #                                   "begin": date,
        #                                   "end": date}
        #
        # # sourceResource.description
        # if record.abstract() is not None:
        #     if len(record.abstract()) > 1:
        #         sourceResource['description'] = []
        #         for description in record.abstract():
        #             sourceResource['description'].append(description)
        #     else:
        #         sourceResource['description'] = record.abstract()
        #
        # # sourceResource.extent
        # if record.extent() is not None:
        #     if len(record.extent()) > 1:
        #         sourceResource['extent'] = []
        #         for extent in record.extent():
        #             sourceResource['extent'].append(extent)
        #     else:
        #         sourceResource['extent'] = record.extent()[0]
        #
        # # sourceResource.format
        # if record.form() is not None:
        #     if len(record.form()) > 1:
        #         sourceResource['format'] = []
        #         for form in record.form():
        #             sourceResource['format'].append(form)
        #     else:
        #         sourceResource['format'] = record.form()[0]
        #
        # # sourceResource.genre
        # if record.genre() is not None:
        #     if len(record.genre()) > 1:
        #         sourceResource['genre'] = []
        #         for genre in record.genre():
        #             genre_elem = {}
        #             for key, value in genre.items():
        #                 if 'term' == key:
        #                     genre_elem['name'] = value
        #                 elif 'valueURI' == key:
        #                     genre_elem['@id'] = value
        #             sourceResource['genre'].append(genre_elem)
        #     else:
        #         genre_elem = {}
        #         for key, value in record.genre()[0].items():
        #             if 'term' == key:
        #                 genre_elem['name'] = value
        #             elif 'valueURI' == key:
        #                 genre_elem['@id'] = value
        #         sourceResource['genre'] = genre_elem
        #
        # # sourceResource.identifier
        # sourceResource['identifier'] = {"@id": record.purl_search(),
        #                                 "text": record.local_identifier()}
        #
        # # sourceResource.language
        # if record.language() is not None:
        #     language_list = []
        #     for language in record.language():
        #         if len(language) > 1:
        #             language_dict = {"name": language['text'],
        #                              "iso_639_3": language['code']}
        #         else:
        #             if 'text' in language.keys():
        #                 language_dict = {"name": language['text']}
        #             else:
        #                 pass
        #         language_list.append(language_dict)
        #     sourceResource['language'] = language_list
        #
        # # sourceResource.place : sourceResource['spatial']
        # geo_code_list = record.geographic_code()
        # if geo_code_list is not None:
        #     sourceResource['spatial'] = []
        #     for geo_code in geo_code_list:
        #         code, lat, long, label = assets.tgn_cache(geo_code)
        #         sourceResource['spatial'].append({"lat": lat,
        #                                           "long": long,
        #                                           "name": label,
        #                                           "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License."})
        #
        #         # tgn_prefix = 'http://vocab.getty.edu/tgn/'
        #
        #         '''
        #         # Implementation using the schema.org namespace
        #         # tgn_geometry = geo_code + '-geometry.jsonld'
        #         # geometry = requests.get(tgn_prefix + tgn_geometry)
        #         # geometry_json = json.loads(geometry.text)
        #         # lat = geometry_json['http://schema.org/latitude']['@value']
        #         # long = geometry_json['http://schema.org/longitude']['@value']
        #         '''
        #
        #         # tgn_place = geo_code + '-place.jsonld'
        #         # place = requests.get(tgn_prefix + tgn_place)
        #         # if place.status_code == 200:
        #         #    place_json = json.loads(place.text)
        #         #    lat = place_json['http://www.w3.org/2003/01/geo/wgs84_pos#lat']['@value']
        #         #    long = place_json['http://www.w3.org/2003/01/geo/wgs84_pos#long']['@value']
        #         #    sourceResource['spatial'].append({ "lat": lat,
        #         #                                       "long": long,
        #         #                                       "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License." })
        #
        # # sourceResource.publisher
        # if record.publisher() is not None:
        #     if len(record.publisher()) > 1:
        #         sourceResource['publisher'] = []
        #         for publisher in record.publisher():
        #             sourceResource['publisher'].append(publisher)
        #     else:
        #         sourceResource['publisher'] = record.publisher()[0]
        #
        # # sourceResource.relation
        #
        # # sourceResource.isReplacedBy
        #
        # # sourceResource.replaces
        #
        # # sourceResource.rights
        # if record.rights() is not None:
        #     if len(record.rights()) > 1:
        #         sourceResource['rights'] = {"@id": record.rights()['URI'],
        #                                     "text": record.rights()['text']}
        #     else:
        #         sourceResource['rights'] = record.rights()['text']
        # else:
        #     logging.warning('No sourceResource.rights - {0}'.format(record.pid_search()))
        #     continue
        #
        # # sourceResource.subject
        # try:
        #
        #     if record.subject() is not None:
        #         sourceResource['subject'] = []
        #         for subject in record.subject():
        #             non_alpha_char = re.compile("^[^a-zA-Z]+$")
        #             if non_alpha_char.match(subject['text']) is None:
        #
        #                 if 'valueURI' in subject.keys():
        #                     sourceResource['subject'].append({"@id": subject['valueURI'],
        #                                                       "name": subject['text']})
        #                 else:
        #                     sourceResource['subject'].append({"name": subject['text']})
        #             else:
        #                 pass
        #
        # except TypeError as err:
        #     logging.warning('sourceResource.subject: {0}, {1}\n'.format(err, record.pid_search()))
        #     pass
        #
        # # sourceResource.title
        # if record.title_constructor() is not None:
        #     sourceResource['title'] = record.title_constructor()[0]
        # else:
        #     logging.warning('No sourceResource.title: {0}'.format(record.pid_search()))
        #     continue
        #
        # # sourceResource.type
        # sourceResource['type'] = record.type_of_resource()
        #
        # # aggregation.dataProvider
        # data_provider = dprovide
        #
        # # aggregation.intermediateProvider #TODO
        #
        # # aggregation.isShownAt
        #
        # # aggregation.preview
        # pid = record.pid_search()
        # preview = assets.thumbnail_service(pid, tn)
        #
        # # aggregation.provider

        docs.append({"@context": "http://api.dp.la/items/context",
                     "sourceResource": sourceResource,
                     "aggregatedCHO": "#sourceResource",
                     "dataProvider": data_provider,
                     "isShownAt": record.metadata.purl,
                     #"preview": preview,
                     "provider": PROVIDER})


    #write_json_ld(docs)
    print(json.dumps(docs, indent=2))  # test
