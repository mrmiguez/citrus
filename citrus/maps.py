"""
Maps define how data exposed through `citrus.Scenarios` are manipulated to build `citrus.SourceResource` objects

`citrus.cli.transform` read the configuration file `citrus_scenarios.cfg`.to determine which map to apply for which source
"""

from citrus.source_resource import SourceResource


def dc_standard_map(record):
    sr = SourceResource()
    sr.contributor = record.contributor
    sr.creator = record.creator
    sr.date = record.date
    sr.description = record.description
    sr.format = record.format
    sr.identifier = record.harvest_id
    sr.language = record.language
    sr.place = record.place
    sr.publisher = record.publisher
    sr.rights = record.rights
    sr.subject = record.subject
    sr.title = record.title
    sr.type = record.type
    return sr


def qdc_standard_map(record):
    sr = dc_standard_map(record)
    sr.alternative = record.alternative
    sr.abstract = record.abstract
    sr.collection = record.is_part_of
    sr.extent = record.extent
    return sr


def mods_standard_map(record):
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
    sr.place = record.place
    sr.publisher = record.publisher
    sr.rights = record.rights
    sr.subject = record.subject
    sr.title = record.title
    sr.type = record.type
    return sr
