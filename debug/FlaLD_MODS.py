#!/usr/bin/env python3

import sys
import json
import requests
from pymods import MODS, FSUDL
from lxml import etree #test

def write_json_ld(docs):
    with open('testData/fsu_digital_library-1.json', 'w') as jsonOutput:
        json.dump(docs, jsonOutput)


with open(sys.argv[1], encoding='utf-8') as data_in:
    records = MODS(data_in)
    docs = []
    for record in records.record_list:
        #print(FSUDL.pid_search(record)) #test
        sourceResource = {}

        # sourceResource.alternative
        if MODS.title_constructor(record)[1:] is not None:
            sourceResource['alternative'] = []
            if len(MODS.title_constructor(record)[1:]) >= 1:
                for alternative_title in MODS.title_constructor(record)[1:]:
                    sourceResource['alternative'].append(alternative_title)

        # sourceResource.collection
        if MODS.collection(record) is not None:
            collection = MODS.collection(record)
            sourceResource['collection'] = {}
            if 'title' in collection.keys():
                sourceResource['collection']['name'] = collection['title']
            if 'location' in collection.keys():
                sourceResource['collection']['host'] = collection['location']
            if 'url' in collection.keys():
                sourceResource['collection']['_:id'] = collection['url']

        # sourceResource.contributor
        try: #debug

            if MODS.name_constructor(record) is not None:
                sourceResource['contributor'] = []
                for name in MODS.name_constructor(record):

                    if all(key in name.keys() for key in ('roleText' or 'roleCode')):
                        if name['roleText'] != 'Creator':
                            if 'valueURI' in name.keys():
                                sourceResource['contributor'].append({ "@id": name['valueURI'],
                                                                   "name": name['text'] })
                            else:
                                sourceResource['contributor'].append({ "name": name['text'] })
                        elif name['roleCode'] != 'cre':
                            if 'valueURI' in name.keys():
                                sourceResource['contributor'].append({ "@id": name['valueURI'],
                                                                   "name": name['text'] })
                            else:
                                sourceResource['contributor'].append({ "name": name['text'] })

                    else:
                        if 'valueURI' in name.keys():
                            sourceResource['contributor'].append({"@id": name['valueURI'],
                                                                  "name": name['text']} )
                        else:
                            sourceResource['contributor'].append({"name": name['text']} )

                if len(sourceResource['contributor']) < 1:
                    del sourceResource['contributor']

        except KeyError as err: #debug
            with open('errorDump.txt', 'a') as dumpFile:
                dumpFile.write('AttributeError - sourceResource.contributor: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
                dumpFile.write('{0}\n'.format(name))
                #dumpFile.write(etree.tostring(record).decode('utf-8'))
            pass

        #except AttributeError as err: #debug
        #    with open('errorDump.txt', 'a') as dumpFile:
        #        dumpFile.write('AttributeError - sourceResource.contributor: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
        #        dumpFile.write('{0}\n'.format(name))
        #        dumpFile.write(etree.tostring(record).decode('utf-8'))
        #    pass

        # sourceResource.creator
        #try:  # debug

        if MODS.name_constructor(record) is not None:
            sourceResource['creator'] = []
            for name in MODS.name_constructor(record):

                if all(key in name.keys() for key in ('roleText' or 'roleCode')):
                    if name['roleText'] == 'Creator':
                        if 'valueURI' in name.keys():
                            sourceResource['creator'].append({ "@id": name['valueURI'],
                                                               "name": name['text'] })
                        else:
                            sourceResource['creator'].append({ "name": name['text'] })
                    elif name['roleCode'] == 'cre':
                        if 'valueURI' in name.keys():
                            sourceResource['creator'].append({ "@id": name['valueURI'],
                                                               "name": name['text'] })
                        else:
                            sourceResource['creator'].append({ "name": name['text'] })
                else:
                    pass

        #except AttributeError as err: # debug
        #    with open('errorDump.txt', 'a') as dumpFile:
        #        dumpFile.write('AttributeError - sourceResource.creator: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
        #        dumpFile.write('{0}\n'.format(name))
        #        dumpFile.write(etree.tostring(record).decode('utf-8'))
        #    pass

        # sourceResource.date
        if MODS.date_constructor(record) is not None:
            date = MODS.date_constructor(record)
            if ' - ' in date:
                sourceResource['date'] = { "displayDate": date,
                                           "begin": date[0:4],
                                           "end": date[-4:] }
            else:
                sourceResource['date'] = { "displayDate": date,
                                           "begin": date,
                                           "end": date }

        # sourceResource.description
        if MODS.abstract(record) is not None:
            if len(MODS.abstract(record)) > 1:
                sourceResource['description'] = []
                for description in MODS.abstract(record):
                    sourceResource['description'].append(description)
            else:
                sourceResource['description'] = MODS.abstract(record)

        # sourceResource.extent
        if MODS.extent(record) is not None:
            if len(MODS.extent(record)) > 1:
                sourceResource['extent'] = []
                for extent in MODS.extent(record):
                    sourceResource['extent'].append(extent)
            else:
                sourceResource['extent'] = MODS.extent(record)[0]

        # sourceResource.format
        if MODS.form(record) is not None:
            if len(MODS.form(record)) > 1:
                sourceResource['format'] = []
                for form in MODS.form(record):
                    sourceResource['format'].append(form)
            else:
                sourceResource['format'] = MODS.form(record)[0]

        # sourceResource.genre
        if MODS.genre(record) is not None:
            if len(MODS.genre(record)) > 1:
                sourceResource['genre'] = []
                for genre in MODS.genre(record):
                    genre_elem = {}
                    for key, value in genre.items():
                        if 'term' == key:
                            genre_elem['name'] = value
                        elif 'valueURI' == key:
                            genre_elem['@id'] = value
                    sourceResource['genre'].append(genre_elem)
            else:
                genre_elem = {}
                for key, value in MODS.genre(record)[0].items():
                    if 'term' == key:
                        genre_elem['name'] = value
                    elif 'valueURI' == key:
                        genre_elem['@id'] = value
                sourceResource['genre'] = genre_elem

        # sourceResource.identifier
        sourceResource['identifier'] = { "@id": FSUDL.purl_search(record),
                                         "text": FSUDL.local_identifier(record) }

        # sourceResource.language
        #try: #debug

        if MODS.language(record) is not None:
            language_list = []
            for language in MODS.language(record):
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

        #except KeyError as err: #debug
        #    with open('errorDump.txt', 'a') as dumpFile:
        #        dumpFile.write('KeyError - sourceResource.language: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
        #        dumpFile.write('{0}\n'.format(language))
        #        dumpFile.write(etree.tostring(record).decode('utf-8'))
        #    pass

        # sourceResource.sourceResource.place : sourceResource['spatial']
        #try:

        geo_code_list = MODS.geographic_code(record)
        if geo_code_list is not None:
            sourceResource['spatial'] = []
            for geo_code in geo_code_list:
                tgn_prefix = 'http://vocab.getty.edu/tgn/'

                '''
                # Implementation using the schema.org namespace
                # tgn_geometry = geo_code + '-geometry.jsonld'
                # geometry = requests.get(tgn_prefix + tgn_geometry)
                # geometry_json = json.loads(geometry.text)
                # lat = geometry_json['http://schema.org/latitude']['@value']
                # long = geometry_json['http://schema.org/longitude']['@value']
                '''

                tgn_place = geo_code + '-place.jsonld'
                place = requests.get(tgn_prefix + tgn_place)
                if place.status_code == 200:
                    place_json = json.loads(place.text)
                    lat = place_json['http://www.w3.org/2003/01/geo/wgs84_pos#lat']['@value']
                    long = place_json['http://www.w3.org/2003/01/geo/wgs84_pos#long']['@value']
                    sourceResource['spatial'].append({ "lat": lat,
                                                       "long": long,
                                                       "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN)® which is made available under the ODC Attribution License." })

        #except KeyError as err: #debug
        #    with open('errorDump.txt', 'a') as dumpFile:
        #        dumpFile.write('KeyError - sourceResource.sourceResource.place: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
        #        dumpFile.write(etree.tostring(record).decode('utf-8'))
        #    pass

        # sourceResource.publisher
        if MODS.publisher(record) is not None:
            if len(MODS.publisher(record)) > 1:
                sourceResource['publisher'] = []
                for publisher in MODS.publisher(record):
                    sourceResource['publisher'].append(publisher)
            else:
                sourceResource['publisher'] = MODS.publisher(record)[0]

        # sourceResource.relation

        # sourceResource.isReplacedBy

        # sourceResource.replaces

        # sourceResource.rights
        #try:

        if MODS.rights(record) is not None:
            if len(MODS.rights(record)) > 1:
                sourceResource['rights'] = {"@id": MODS.rights(record)['URI'],
                                            "text": MODS.rights(record)['text']}
            else:
                sourceResource['rights'] = MODS.rights(record)['text']

        #except TypeError as err: #debug
        #    with open('errorDump.txt', 'a') as dumpFile:
        #        dumpFile.write('TypeError - sourceResource.rights: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
        #        dumpFile.write(etree.tostring(record).decode('utf-8'))
        #    pass

        # sourceResource.subject
        try: #debug

            if MODS.subject(record) is not None:
                sourceResource['subject'] = []
                for subject in MODS.subject(record):

                    if 'valueURI' in subject.keys():
                        sourceResource['subject'].append({"@id": subject['valueURI'],
                                                          "name": subject['text'] })
                    else:
                        sourceResource['subject'].append({"name": subject['text'] })

        except TypeError as err: #debug
            with open('errorDump.txt', 'a') as dumpFile:
                dumpFile.write('KeyError - sourceResource.subject: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
                dumpFile.write(etree.tostring(record).decode('utf-8'))
            pass

        # sourceResource.title
        #try: # debug
        sourceResource['title'] = MODS.title_constructor(record)[0]

        #except IndexError: # debug
        #    with open('errorDump.txt', 'a') as dumpFile:
        #        dumpFile.write('IndexError - sourceResource.title: {0}, {1}\n'.format(FSUDL.pid_search(record), err))
        #        dumpFile.write(etree.tostring(record).decode('utf-8'))
        #    pass

        # sourceResource.type
        sourceResource['type'] = MODS.type_of_resource(record)

        # aggregation.dataProvider
        data_provider = "Florida State University Libraries"

        # aggregation.isShownAt

        # aggregation.preview
        pid = FSUDL.pid_search(record)
        preview = "http://fsu.digital.flvc.org/islandora/object/{0}/datastream/TN/view".format(pid)

        # aggregation.provider
        provider = {"name": "TO BE DETERMINED",
                    "@id": "DPLA provides?"}

        docs.append({"@context": "http://api.dp.la/items/context",
                     "sourceResource": sourceResource,
                     "aggregatedCHO": "#sourceResource",
                     "dataProvider": data_provider,
                     "isShownAt": FSUDL.purl_search(record),
                     "preview": preview,
                     "provider": provider})


    #write_json_ld(docs)
    #print(json.dumps(docs, indent=2)) #test
