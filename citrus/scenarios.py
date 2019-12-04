import re
from pymods import OAIReader
import citrus

dc = '{http://purl.org/dc/elements/1.1/}'
dcterms = '{http://purl.org/dc/terms/}'


class Scenario:

    def __init__(self, file_in, org: citrus.Organization):
        self.org = org
        self.records = []
        # self.data_provider = org.data_provider
        # self.thumbnail = org.thumbnail
        # if org.intermediate_provider:
        #     self.intermediate_provider = org.intermediate_provider
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

    def __str__(self):
        return f'{self.__class__.__name__}'


class SSDN_DC(Scenario):

    def __init__(self, file_in, org):
        Scenario.__init__(self, file_in, org)
        self.records = [DC_Record(record) for record in self.records]


class SSDN_QDC(Scenario):

    def __init__(self, file_in, org):
        Scenario.__init__(self, file_in, org)
        self.records = [QDC_Record(record) for record in self.records]


class SSDN_MODS(Scenario):

    def __init__(self, file_in, org):
        Scenario.__init__(self, file_in, org)
        self.records = [MODS_Record(record) for record in self.records]


class CitrusRecord:

    def __init__(self, record):
        self.record = record
        self.oai_id = self.record.oai_urn

    def __str__(self):
        return f'{self.__class__.__name__}, {self.oai_id}'


class DC_Record(CitrusRecord):

    def __init__(self, record):
        CitrusRecord.__init__(self, record)

    @property
    def contributor(self):
        try:
            return [{"name": name} for name in
                    self.record.metadata.get_element('.//{0}contributor'.format(dc), delimiter=';')]
        except TypeError:
            pass

    @property
    def creator(self):
        try:
            return [{"name": name.strip(" ").rstrip("( Contributor )").rstrip("( contributor )")} for name in
                    self.record.metadata.get_element('.//{0}creator'.format(dc), delimiter=';')]
        except TypeError:
            pass

    @property
    def date(self):
        return [date for date in self.record.metadata.get_element('.//{0}date'.format(dc))]

    @property
    def description(self):
        return [description for description in
                self.record.metadata.get_element('.//{0}description'.format(dc), delimiter=';')]

    @property
    def format(self):
        return [ft for ft in self.record.metadata.get_element('.//{0}format'.format(dc))]

    @property
    def identifier(self):
        return [identifier for identifier in self.record.metadata.get_element('.//{0}identifier'.format(dc))]

    @property
    def language(self):
        return [lang for lang in self.record.metadata.get_element('.//{0}language'.format(dc), delimiter=';')]

    @property
    def place(self):
        return [{'name': place} for place in self.record.metadata.get_element('.//{0}coverage'.format(dc))]

    @property
    def publisher(self):
        return [publisher for publisher in self.record.metadata.get_element('.//{0}publisher'.format(dc))]

    # sourceResource.relation

    # sourceResource.isReplacedBy

    # sourceResource.replaces

    @property
    def rights(self):
        return [rights for rights in self.record.metadata.get_element('.//{0}rights'.format(dc))]

    @property
    def subject(self):
        return [sub for sub in self.record.metadata.get_element('.//{0}subject'.format(dc))]

    @property
    def title(self):
        return [title for title in self.record.metadata.get_element('.//{0}title'.format(dc))]

    @property
    def type(self):
        return [t for t in self.record.metadata.get_element('.//{0}type'.format(dc), delimiter=';')]


class QDC_Record(DC_Record):

    def __init__(self, record):
        DC_Record.__init__(self, record)

    @property
    def abstract(self):
        return [abstract for abstract in self.record.metadata.get_element('.//{0}abstract'.format(dcterms))]

    @property
    def alternative(self):
        return [alt for alt in self.record.metadata.get_element('.//{0}alternative'.format(dcterms))]

    # sourceResource.collection

    @property
    def date(self):
        date = None
        date_list = (f'{dcterms}created', f'{dcterms}issued', f'{dcterms}date', f'{dc}date', f'{dcterms}available',
                     f'{dcterms}dateAccepted', f'{dcterms}dateCopyrighted', f'{dcterms}dateSubmitted')
        for d in date_list:
            date = self.record.metadata.get_element(f'.//{d}')
            if date:
                break
        return date

    @property
    def extent(self):
        try:
            return [extent for extent in
                    self.record.metadata.get_element('.//{0}extent'.format(dcterms), delimiter=';')]
        except TypeError:
            pass

    @property
    def place(self):
        return [{'name': place} for place in
                self.record.metadata.get_element('.//{0}spatial'.format(dcterms), delimiter=';')]


class MODS_Record(CitrusRecord):

    def __init__(self, record):
        CitrusRecord.__init__(self, record)

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

    @property
    def creator(self):
        return [{"@id": name.uri, "name": name.text} if name.uri else {"name": name.text} for name in
                self.record.metadata.get_creators]

    @property
    def date(self):
        if self.record.metadata.dates:
            date = self.record.metadata.dates[0].text
            if ' - ' in date:
                return {"displayDate": date,
                        "begin": date[0:4],
                        "end": date[-4:]}
            else:
                return {"displayDate": date,
                        "begin": date,
                        "end": date}

    @property
    def description(self):
        return [abstract.text for abstract in self.record.metadata.abstract]

    @property
    def extent(self):
        return self.record.metadata.extent

    @property
    def format(self):
        return [{'name': genre.text, '@id': genre.uri} if genre.uri else {'name': genre.text} for genre in
                self.record.metadata.genre]

    @property
    def identifier(self):
        return self.record.metadata.purl[0]

    @property
    def language(self):
        return [{"name": lang.text, "iso_639_3": lang.code} for lang in self.record.metadata.language]

    @property
    def place(self):
        for subject in self.record.metadata.subjects:
            for c in subject.elem.getchildren():
                if 'eographic' in c.tag:
                    return {"name": subject.text}

    @property
    def publisher(self):
        return self.record.metadata.publisher

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

    @property
    def type(self):
        return self.record.metadata.type_of_resource
