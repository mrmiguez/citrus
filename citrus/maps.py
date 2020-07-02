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
    if record.contributor:
        sr.contributor = [{'name': name} for name in record.contributor]
    sr.creator = [{'name': name} for name in record.creator if record.creator]
    sr.date = record.date
    sr.description = record.description
    sr.format = record.format
    sr.identifier = record.harvest_id
    sr.language = record.language
    if record.place:
        sr.spatial = [{'name': place} for place in record.place]
    sr.publisher = record.publisher
    sr.rights = record.rights
    if record.subject:
        sr.subject = [{'name': subject} for subject in record.subject]
    sr.title = record.title
    sr.type = record.type
    tn = None
    yield sr, tn


def qdc_standard_map(record):
    logger.debug(f'Loaded {__name__}.qdc_standard_map map')
    for dc_rec, _ in dc_standard_map(record):
        sr = dc_rec
    sr.alternative = record.alternative
    sr.abstract = record.abstract
    sr.collection = record.is_part_of
    sr.extent = record.extent
    tn = None
    yield sr, tn


def mods_standard_map(record):
    logger.debug(f'Loaded {__name__}.mods_standard_map map')
    sr = SourceResource()
    sr.alternative = record.alternative
    try:
        sr.collection = record.collection.title
    except AttributeError:
        logger.info(f"No collection title - {record.harvest_id}")
        pass
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
    tn = None
    yield sr, tn
