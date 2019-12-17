from citrus import SourceResource


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
    sr.collection = record.collection
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
