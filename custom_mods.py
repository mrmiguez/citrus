import re
import logging
import requests
from pymods import OAIReader
from bs4 import BeautifulSoup

# custom functions and variables
import assets
from citrus import nameSpace_default
from citrus_config import PROVIDER, VERBOSE

dc = nameSpace_default['dc']


def FlMem(file_in, tn, dprovide, iprovide=None):
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
            logging.debug(oai_id)
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

            # # sourceResource.identifier  # TODO: commented temp for testing
            # dPantherPURL = re.compile('dpService/dpPurlService/purl')
            # identifier = record.metadata.get_element('.//{0}identifier'.format(dc))
            # try:
            #     for ID in identifier:
            #         PURL = dPantherPURL.search(ID)
            #
            #         try:
            #             PURL_match = PURL.string
            #
            #         except AttributeError as err:
            #             logging.warning(
            #                 'sourceResource.identifier: {0} - {1}'.format(err,
            #                                                               oai_id))
            #             pass
            #     sourceResource['identifier'] = PURL_match
            #
            # except TypeError as err:
            #     logging.error(
            #         'sourceResource.identifier: {0} - {1}'.format(err,
            #                                                       oai_id))
            #     continue

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
                logging.error('No sourceResource.rights - {0}'.format(oai_id))
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
                logging.error('No sourceResource.rights - {0}'.format(oai_id))
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

            # # aggregation.preview  # TODO: commented temp for testing
            # try:
            #     preview = assets.thumbnail_service(PURL_match, tn)
            # except UnboundLocalError as err:
            #     logging.error('aggregation.preview: {0} - {1}'.format(err, oai_id))
            #     continue

            # aggregation.provider

            try:
                docs.append({"@context": "http://api.dp.la/items/context",
                             "sourceResource": sourceResource,
                             "aggregatedCHO": "#sourceResource",
                             "dataProvider": data_provider,
                             # "isShownAt": PURL_match,  #TODO temp
                             # "preview": preview,  # TODO temp
                             "provider": PROVIDER})
            except NameError as err:
                logging.error('aggregation.preview: {0} - {1}'.format(err, oai_id))
                pass

    return docs