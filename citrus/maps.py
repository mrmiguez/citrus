"""
Maps define how data exposed through `citrus.Scenarios` are manipulated to build `citrus.SourceResource` objects

`citrus.cli.transform` read the configuration file `citrus_scenarios.cfg`.to determine which map to apply for which source
"""
import logging

from citrus.source_resource import SourceResource

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def dc_standard_map(record):
    logger.debug(f'Loaded {__name__}.dc_standard_map map')
    sr = SourceResource()
    sr.contributor = [{'name': name} for name in record.contributor if record.contributor]
    sr.creator = [{'name': name} for name in record.creator if record.creator]
    sr.date = record.date
    sr.description = record.description
    sr.format = record.format
    sr.identifier = record.harvest_id
    sr.language = record.language
    sr.spatial = [{'name': place} for place in record.place if record.place]
    sr.publisher = record.publisher
    sr.rights = record.rights
    sr.subject = [{'name': subject} for subject in record.subject if record.subject]
    sr.title = record.title
    sr.type = record.type
    return sr


def qdc_standard_map(record):
    logger.debug(f'Loaded {__name__}.qdc_standard_map map')
    sr = dc_standard_map(record)
    sr.alternative = record.alternative
    sr.abstract = record.abstract
    sr.collection = record.is_part_of
    sr.extent = record.extent
    return sr


def mods_standard_map(record):
    logger.debug(f'Loaded {__name__}.mods_standard_map map')
    sr = SourceResource()
    sr.alternative = record.alternative
    sr.collection = record.collection.title
    sr.contributor = record.contributor
    sr.creator = record.creator
    sr.date = record.date
    sr.description = record.description
    sr.extent = record.extent
    sr.format = record.format
    sr.identifier = record.harvest_id
    sr.language = record.language
    sr.spatial = record.place
    sr.publisher = record.publisher
    sr.rights = record.rights
    sr.subject = record.subject
    sr.title = record.title
    sr.type = record.type
    return sr
