#!/usr/bin/env python3

import sys
import json
from pymods import OAIReader

PROVIDER = 'FSU'  # temp
dprovide = 'FSU'  # temp


def write_json_ld(docs):
    with open('testData/fsu_digital_library-1.json', 'w') as jsonOutput:
        json.dump(docs, jsonOutput)


with open(sys.argv[1], encoding='utf-8') as data_in:
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

            if record.metadata.names:
                sourceResource['contributor'] = [{"@id": name.uri, "name": name.text}
                                                 for name in record.metadata.names
                                                 if name.role != "Creator"]
        except KeyError as err:
            # logging.warning('sourceResource.contributor: {0}, {1}\n'.format(err, record.pid_search()))  # TODO re-enable logging
            pass

        # sourceResource.creator
        if record.metadata.get_creators:
            sourceResource['creator'] = [{"@id": name.uri, "name": name.text}
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
                                        '@id': genre.valueURI}
                                       for genre in record.metadata.genre]

        # sourceResource.identifier
        sourceResource['identifier'] = {"@id": record.metadata.purl,
                                        "text": record.metadata.iid}

        # sourceResource.language  # TODO - what happens with a multi-language item?
        key_map = {'code': 'iso_639_3', 'text': 'name'}
        if record.metadata.language:
            sourceResource['language'] = [{key_map[lang.type]: lang.text for lang in record.metadata.language}]

        # sourceResource.place : sourceResource['spatial']
        geo_code_list = record.metadata.geographic_code
        if geo_code_list is not None:
            sourceResource['spatial'] = []
            for geo_code in geo_code_list:
                sourceResource['spatial'].append(geo_code)  # test
            #     code, lat, long, label = assets.tgn_cache(geo_code)  # TODO - re-enable
            #     sourceResource['spatial'].append({"lat": lat,
            #                                       "long": long,
            #                                       "name": label,
            #                                       "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License."})

        # sourceResource.publisher
        if record.metadata.publisher:
            sourceResource['publisher'] = record.metadata.publisher

        # sourceResource.relation

        # sourceResource.isReplacedBy

        # sourceResource.replaces

        # sourceResource.rights
        if record.metadata.rights:
            sourceResource['rights'] = [{"@id": rights.uri, "text": rights.text}
                                        for rights in record.metadata.rights]
        # else:  # TODO re-enable logging
        #     logging.warning('No sourceResource.rights - {0}'.format(record.pid_search()))
        #     continue

        # sourceResource.subject
        try:

            if record.metadata.subjects:
                sourceResource['subject'] = [{"@id": subject.uri, "name": subject.text}
                                             for subject in record.metadata.subjects]
        except TypeError as err:
            # logging.warning('sourceResource.subject: {0}, {1}\n'.format(err, record.pid_search()))  # TODO re-enable logging
            pass

        # sourceResource.title
        if record.metadata.titles:
            sourceResource['title'] = record.metadata.titles[0]
        # else:  # TODO - re-enable logging
        #     logging.warning('No sourceResource.title: {0}'.format(record.pid_search()))
        #     continue

        # sourceResource.type
        sourceResource['type'] = record.metadata.type_of_resource

        # aggregation.dataProvider
        data_provider = dprovide

        # aggregation.intermediateProvider  # TODO

        # aggregation.isShownAt

        # aggregation.preview
        pid = record.metadata.pid
        # preview = assets.thumbnail_service(pid, tn)  # TODO - re-enable thumbnail service

        # aggregation.provider

        docs.append({"@context": "http://api.dp.la/items/context",
                     "sourceResource": sourceResource,
                     "aggregatedCHO": "#sourceResource",
                     "dataProvider": data_provider,
                     "isShownAt": record.metadata.purl,
                     #"preview": preview,
                     "provider": PROVIDER})


    #write_json_ld(docs)
    print(json.dumps(docs, indent=2))  # test
