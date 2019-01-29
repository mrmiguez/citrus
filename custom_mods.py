import logging
import re

from pymods import OAIReader

# custom functions and variables
import assets
from citrus import nameSpace_default
from citrus_config import VERBOSE

dc = nameSpace_default['dc']

logger = logging.getLogger(__name__)


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
            for identifier in record.metadata.get_element('.//{0}identifier'.format(dc)):
                if 'http' in identifier:
                    is_shown_at = identifier.replace(identifier.split('/')[2], 'www.floridamemory.com')
                    is_shown_at = is_shown_at.replace('http:', 'https:')
            sourceResource['identifier'] = oai_id.replace(oai_id.split(':')[1], 'www.floridamemory.com')

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

            # sourceResource.rights  # TODO: hard-coding is only temporary
            sourceResource['rights'] = {'@id': 'http://rightsstatements.org/vocab/NoC-US/1.0/'}

            # rights = record.metadata.get_element('.//{0}rights'.format(dc))
            # if rights:
            #     sourceResource['rights'] = [{'text': rights[0]}]
            # else:
            #     logger.error('No sourceResource.rights - {0}'.format(oai_id))
            #     # continue  # TODO renable for prod
            #     pass  # local test

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

            # aggregation.intermediateProvider

            # aggregation.isShownAt

            # aggregation.preview
            preview = None
            try:
                preview = assets.thumbnail_service(is_shown_at, tn)
            except UnboundLocalError as err:
                logger.error('aggregation.preview: {0} - {1}'.format(err, oai_id))
                pass

            # aggregation.provider
            try:
                if is_shown_at:
                    doc = assets.build(oai_id, sourceResource, data_provider, is_shown_at, preview, iprovide)
                else:
                    logger.error('No aggregation.isShownAt - {0}'.format(oai_id))
                    continue

                docs.append(doc)
            except UnboundLocalError:
                continue

    return docs
