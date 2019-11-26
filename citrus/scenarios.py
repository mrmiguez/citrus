import re
from pymods import OAIReader
from .exceptions import *

nameSpace_default = {None: '{http://www.loc.gov/mods/v3}',
                     'oai_dc': '{http://www.openarchives.org/OAI/2.0/oai_dc/}',
                     'dc': '{http://purl.org/dc/elements/1.1/}',
                     'mods': '{http://www.loc.gov/mods/v3}',
                     'dcterms': '{http://purl.org/dc/terms/}',
                     'xlink': '{http://www.w3.org/1999/xlink}',
                     'repox': '{http://repox.ist.utl.pt}',
                     'oai_qdc': '{http://worldcat.org/xmlschemas/qdc-1.0/}'}

dc = nameSpace_default['dc']
dcterms = nameSpace_default['dcterms']


class Scenario:

    def __init__(self, file_in, tn=None, dprovide=None, iprovide=None):
        self.tn = tn
        self.dprovide = dprovide
        self.iprovide = iprovide
        self.records = []
        with open(file_in, encoding='utf-8') as data_in:
            records = OAIReader(data_in)
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
                self.records.append(record)

    def __iter__(self):
        for record in self.records:
            yield record

    def __len__(self):
        return len(self.records)


class SSDN_DC(Scenario):

    def __init__(self, file_in, tn, dprovide, iprovide=None):
        Scenario.__init__(self, file_in, tn, dprovide, iprovide=None)
        self.records = [DC_Record(record) for record in self.records]


class SSDN_QDC(Scenario):

    def __init__(self, file_in, tn, dprovide, iprovide=None):
        Scenario.__init__(self, file_in, tn, dprovide, iprovide=None)
        self.records = [QDC_Record(record) for record in self.records]


class SSDN_MODS(Scenario):

    def __init__(self, file_in, tn, dprovide, iprovide=None):
        Scenario.__init__(self, file_in, tn, dprovide, iprovide=None)
        self.records = [MODS_Record(record) for record in self.records]


class CitrusRecord:

    def __init__(self, record):
        self.record = record
        self.oai_id = self.record.oai_urn


class DC_Record(CitrusRecord):

    @property
    def contributor(self):
        return [{"name": name} for name in self.record.metadata.get_element('.//{0}contributor'.format(dc), delimiter=';')]

    def creator(self, record):
        '''
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
        '''

    @property
    def date(self):
        date = self.record.metadata.get_element('.//{0}date'.format(dc))
        if date:
            return {"begin": date[0], "end": date[0], "displayDate": date[0]}

    @property
    def description(self):
        return self.record.metadata.get_element('.//{0}description'.format(dc), delimiter=';')

    @property
    def format(self):
        return self.record.metadata.get_element('.//{0}format'.format(dc))

    def identifier(self, record):
        '''
        dPantherPURL = re.compile('http://dpanther.fiu.edu/dpService/dpPurlService')
        dPantherURL = re.compile('http://dpanther')
        identifier = record.metadata.get_element('.//{0}identifier'.format(dc))
        try:
            for ID in identifier:
                if dPantherPURL.search(ID):
                    PURL_match = ID
                    sourceResource['identifier'] = ID
                    break
                elif dPantherURL.search(ID):
                    sourceResource['identifier'] = ID
                    logger.warning('sourceResource.identifier: {0} - {1}'.format('Not a PURL',
                                                                                 oai_id))
            is_shown_at = sourceResource['identifier']

        except (TypeError, UnboundLocalError) as err:
            logger.error(
                'sourceResource.identifier: {0} - {1}'.format(err,
                                                              oai_id))
            continue
        '''

    def language(self, record):
        '''
        if record.metadata.get_element('.//{0}language'.format(dc)):
            sourceResource['language'] = []
            for element in record.metadata.get_element(
                    './/{0}language'.format(dc), delimiter=';'):
                if len(element) > 3:
                    sourceResource['language'].append({"name": element})
                else:
                    sourceResource['language'].append({"iso_639_3": element})
        '''

    @property
    def place(self):
        return [{'name': place} for place in self.record.metadata.get_element('.//{0}coverage'.format(dc))]

    @property
    def publisher(self):
        return self.record.metadata.get_element('.//{0}publisher'.format(dc))

    # sourceResource.relation

    # sourceResource.isReplacedBy

    # sourceResource.replaces

    @property
    def rights(self):
        rights = self.record.metadata.get_element('.//{0}rights'.format(dc))
        if rights:
            return [{'text': rights[0]}]
        '''
        else:
            logger.error('No sourceResource.rights - {0}'.format(oai_id))
            continue
        '''

    def subject(self, record):
        '''
        if record.metadata.get_element('.//{0}subject'.format(dc)):
            sourceResource['subject'] = []
            for term in record.metadata.get_element('.//{0}subject'.format(dc),
                                                    delimiter=';'):
                term = re.sub("\( lcsh \)$", '', term)
                if len(term) > 0:
                    sourceResource['subject'].append({"name": term.strip(" ")})
        '''

    @property
    def title(self):
        return self.record.metadata.get_element('.//{0}title'.format(dc))
        '''
        else:
            logger.error('No sourceResource.rights - {0}'.format(oai_id))
            continue
        '''

    @property
    def type(self):
        return self.record.metadata.get_element('.//{0}type'.format(dc), delimiter=';')

    # webResource.fileFormat

    # aggregation.dataProvider
    # data_provider = dprovide


class QDC_Record(DC_Record):

    def __init__(self, record):
        DC_Record.__init__(self, record)

    # def abstract(self, record):
    #

    @property
    def alternative(self):
        alt_title = self.record.metadata.get_element('.//{0}alternative'.format(dcterms))
        if alt_title:
            return alt_title

    # sourceResource.collection

    @property
    def date(self):
        date = self.record.metadata.get_element('.//{0}created'.format(dcterms))
        if date is None:  # TODO: there has to be a better way to do this
            date = self.record.metadata.get_element('.//{0}issued'.format(dcterms))
        if date is None:
            date = self.record.metadata.get_element('.//{0}date'.format(dcterms))
        if date is None:
            date = self.record.metadata.get_element('.//{0}date'.format(dc))
        if date is None:
            date = self.record.metadata.get_element('.//{0}available'.format(dcterms))
        if date is None:
            date = self.record.metadata.get_element('.//{0}dateAccepted'.format(dcterms))
        if date is None:
            date = self.record.metadata.get_element('.//{0}dateCopyrighted'.format(dcterms))
        if date is None:
            date = self.record.metadata.get_element('.//{0}dateSubmitted'.format(dcterms))

        if date is not None:
            return {"begin": date[0], "end": date[0], "displayDate": date[0]}

    def description(self, record):
        '''
        description = []
        if record.metadata.get_element(
                './/{0}description'.format(dc)) is not None:
            for item in record.metadata.get_element(
                    './/{0}description'.format(dc)):
                description.append(item)
        if record.metadata.get_element(
                './/{0}abstract'.format(dcterms)) is not None:
            for item in record.metadata.get_element(
                    './/{0}abstract'.format(dcterms)):
                description.append(item)
        if description:
            sourceResource['description'] = description
        '''

    @property
    def extent(self):
        return self.record.metadata.get_element('.//{0}extent'.format(dcterms), delimiter=';')

    # sourceResource.format

    @property
    def place(self):
        try:
            return [{'name': place} for place in self.record.metadata.get_element('.//{0}spatial'.format(dcterms), delimiter=';')]
        except TypeError as e:
            raise SSDN_QDCException(e)

    # webResource.fileFormat
    #  TODO: file_format kicked out of SR.genre

    # aggregation.dataProvider
    # data_provider = dprovide


class MODS_Record(CitrusRecord):

    def alternative(self, record):
        '''
        if len(record.metadata.titles) > 1:
            sourceResource['alternative'] = []
            if len(record.metadata.titles[1:]) >= 1:
                for alternative_title in record.metadata.titles[1:]:
                    sourceResource['alternative'].append(alternative_title)
        '''

    # sourceResource.collection

    def contributor(self, record):
        '''
        try:

            for name in record.metadata.names:
                if name.role.text != 'Creator' and name.role.code != 'cre' and name.role.text is not None and name.role.code is not None:
                    return [{"@id": name.uri, "name": name.text}
                                                     if name.uri else
                                                     {"name": name.text}]
        except KeyError as err:
            logger.error('sourceResource.contributor: {0}, {1}'.format(err, record.oai_urn))
            pass
        '''

    def creator(self, record):
        name_list = []
        if record.metadata.get_creators:
            for name in record.metadata.get_creators:
                name_list.append(name)
        if record.metadata.names:
            for name in record.metadata.names:
                if name.role.text is None or name.role.code is None:
                    name_list.append(name)
        return [{"@id": name.uri, "name": name.text} if name.uri else {"name": name.text} for name in name_list]

    def date(self, record):
        if record.metadata.dates:
            date = record.metadata.dates[0].text
            if ' - ' in date:
                return {"displayDate": date,
                        "begin": date[0:4],
                        "end": date[-4:]}
            else:
                return {"displayDate": date,
                        "begin": date,
                        "end": date}

    def description(self, record):
        if record.metadata.abstract:
            return [abstract.text for abstract in record.metadata.abstract]
        '''
        try:
            for toc in record.metadata.iterfind('.//{http://www.loc.gov/mods/v3}tableOfContents'):
                sourceResource['description'].append(toc.text)
        except KeyError:
            sourceResource['description'] = [toc.text for toc
                                             in record.metadata.findall('.//{http://www.loc.gov/mods/v3}tableOfContents')]
        '''

    def extent(self, record):
        if record.metadata.extent:
            return record.metadata.extent

    def format(self, record):
        if record.metadata.genre:
            return [{'name': genre.text, '@id': genre.uri} if genre.uri else {'name': genre.text} for genre in
                    record.metadata.genre]

    def identifier(self, record):
        '''
        try:
            sourceResource['identifier'] = record.metadata.purl[0]
        except IndexError as err:
            logger.error('sourceResource.identifier: {0}, {1}'.format(err, record.oai_urn))
            continue
        '''

    def language(self, record):
        '''
        try:
            if record.metadata.language:
                return [{"name": lang.text, "iso_639_3": lang.code} for lang in record.metadata.language]
        except AttributeError as err:
            logger.error('sourceResource.language: {0}, {1}'.format(err, record.oai_urn))
            pass
        '''

    def place(self, record):
        for subject in record.metadata.subjects:
            for c in subject.elem.getchildren():
                if 'eographic' in c.tag:
                    return {"name": subject.text}

    def publisher(self, record):
        if record.metadata.publisher:
            return record.metadata.publisher

    # sourceResource.relation

    # sourceResource.isReplacedBy

    # sourceResource.replaces

    def rights(self, record):
        '''
        if record.metadata.rights:
            return [{"@id": rights.text} if "http://rightsstatements.org" in rights.text else {"text": rights.text} for rights in record.metadata.rights[:2]]
            # slicing isn't ideal here since it depends on element order
        else:
            logger.error('No sourceResource.rights - {0}'.format(record.oai_urn))
            continue
        '''

    def subject(self, record):
        '''
        try:

            if record.metadata.subjects:
                sourceResource['subject'] = []
                for subject in record.metadata.subjects:
                    for child in subject.elem:
                        if 'eographic' not in child.tag:
                            sourceResource['subject'].append({"name": subject.text})
        except (TypeError, IndexError) as err:
            logger.error('sourceResource.subject: {0}, {1}'.format(err, record.oai_urn))
            pass
        '''

    def title(self, record):
        '''
        if record.metadata.titles:
            sourceResource['title'] = ['{}'.format(record.metadata.titles[0])]
        else:
            logger.error('No sourceResource.title: {0}'.format(record.oai_urn))
            continue
        '''

    def type(self, record):
        return record.metadata.type_of_resource

    # aggregation.dataProvider
    # data_provider = dprovide
