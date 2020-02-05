import dateparser

from citrus import SourceResource


def dlis_ia_map(rec):
    sr = SourceResource()
    try:
        if isinstance(rec.contributor, list):
            sr.contributor = [{'name': name.strip('.')} for name in rec.contributor]
        else:
            sr.contributor = [{'name': rec.contributor.strip('.')}]
    except KeyError:
        pass
    try:
        if isinstance(rec.creator, list):
            sr.creator = [{'name': name.strip('.')} for name in rec.creator]
        else:
            sr.creator = [{'name': rec.creator.strip('.')}]
    except KeyError:
        pass
    try:
        if rec.date:
            d = dateparser.parse(rec.date, languages=['en']).date().isoformat()
            sr.date = {"begin": d, "end": d, "displayDate": d}
    except KeyError:
        pass
    try:
        if rec.description:
            sr.description = rec.description.strip(' ')
    except KeyError:
        pass
    sr.identifier = 'https://archive.org/details/{}'.format(rec.identifier)
    try:
        if rec.language:
            sr.language = rec.language
    except KeyError:
        pass
    sr.rights = {'@id': 'http://rightsstatements.org/vocab/NoC-US/1.0/'}
    try:
        if isinstance(rec.subject, list):
            sr.subject = [{'name': sub.strip('.')} for sub in rec.subject]
        else:
            sr.subject = [{'name': rec.subject.strip('.')}]
    except KeyError:
        pass
    if rec.title:
        sr.title = rec.title
    return sr.data
