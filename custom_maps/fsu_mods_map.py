from citrus import SourceResource, SourceResourceRequiredElementException


def fsu_mods_map(rec):
    sr = SourceResource()
    # sr.alternative = rec.alternative
    # sr.collection = rec.collection
    # sr.contributor = rec.contributor
    # sr.creator = rec.creator
    # sr.date = rec.date
    # sr.description = rec.description
    # sr.extent = rec.extent
    # sr.format = rec.format
    try:
        sr.identifier = rec.identifier
    except IndexError:
        pass
    # sr.language = rec.language
    # sr.place = rec.place
    # sr.publisher = rec.publisher
    try:
        sr.rights = rec.rights
    except SourceResourceRequiredElementException:
        pass
    # sr.subject = rec.subject
    # sr.title = rec.title
    # sr.type = rec.type
    return sr
