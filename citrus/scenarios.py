from pymods import OAIReader

dc = '{http://purl.org/dc/elements/1.1/}'
dcterms = '{http://purl.org/dc/terms/}'


class Scenario:

    def __init__(self, xml_path):
        """
        Generic class for parsing OIA-PMH XML. Serves as a iterable container for pymods.Records at self.records
        :param xml_path: Path to an XML file of OAI-PMH records
        """
        self.records = []
        with open(xml_path, encoding='utf-8') as data_in:
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

    def __init__(self, xml_path):
        """
        Parser and container for citrus.DC_Record records
        :param xml_path: Path to an XML file of oai_dc records
        """
        Scenario.__init__(self, xml_path)
        self.records = [DC_Record(record) for record in self.records]


class SSDN_QDC(Scenario):

    def __init__(self, xml_path):
        """
        Parser and container for citrus.QDC_Record records
        :param xml_path: Path to an XML file of oai_qdc records
        """
        Scenario.__init__(self, xml_path)
        self.records = [QDC_Record(record) for record in self.records]


class SSDN_MODS(Scenario):

    def __init__(self, xml_path):
        """
        Parser and container for citrus.MODS_Record records
        :param xml_path: Path to an XML file of OAI-PMH MODS records
        """
        Scenario.__init__(self, xml_path)
        self.records = [MODS_Record(record) for record in self.records]


class CitrusRecord:

    def __init__(self, record):
        """
        Generic class for single records. Makes record OAI-PMH identifier available through self.oai_id attribute
        :param record: Generic record
        """
        self.record = record
        self.oai_id = self.record.oai_urn

    def __str__(self):
        return f'{self.__class__.__name__}, {self.oai_id}'


class DC_Record(CitrusRecord):

    def __init__(self, record):
        """
        Dublin Core record class. Element text is available through self.element properties
        :param record: oai_dc record
        """
        CitrusRecord.__init__(self, record)

    @property
    def contributor(self):
        try:
            return [{"name": name} for name in
                    self.record.metadata.get_element('.//{0}contributor'.format(dc), delimiter=';')]
        except TypeError:
            return None

    @property
    def creator(self):
        try:
            return [{"name": name.strip(" ").rstrip("( Contributor )").rstrip("( contributor )")} for name in
                    self.record.metadata.get_element('.//{0}creator'.format(dc), delimiter=';')]
        except TypeError:
            return None

    @property
    def date(self):
        try:
            return [date for date in self.record.metadata.get_element('.//{0}date'.format(dc))]
        except TypeError:
            return None

    @property
    def description(self):
        try:
            return [description for description in
                    self.record.metadata.get_element('.//{0}description'.format(dc), delimiter=';')]
        except TypeError:
            return None

    @property
    def format(self):
        try:
            return [ft for ft in self.record.metadata.get_element('.//{0}format'.format(dc))]
        except TypeError:
            return None

    @property
    def identifier(self):
        try:
            return [identifier for identifier in self.record.metadata.get_element('.//{0}identifier'.format(dc))]
        except TypeError:
            return None

    @property
    def language(self):
        try:
            return [lang for lang in self.record.metadata.get_element('.//{0}language'.format(dc), delimiter=';')]
        except TypeError:
            return None

    @property
    def place(self):
        try:
            return [{'name': place} for place in self.record.metadata.get_element('.//{0}coverage'.format(dc))]
        except TypeError:
            return None

    @property
    def publisher(self):
        try:
            return [publisher for publisher in self.record.metadata.get_element('.//{0}publisher'.format(dc))]
        except TypeError:
            return None

    # sourceResource.relation

    # sourceResource.isReplacedBy

    # sourceResource.replaces

    @property
    def rights(self):
        try:
            return [rights for rights in self.record.metadata.get_element('.//{0}rights'.format(dc))]
        except TypeError:
            return None

    @property
    def subject(self):
        try:
            return [sub for sub in self.record.metadata.get_element('.//{0}subject'.format(dc))]
        except TypeError:
            return None

    @property
    def title(self):
        try:
            return [title for title in self.record.metadata.get_element('.//{0}title'.format(dc))]
        except TypeError:
            return None

    @property
    def type(self):
        try:
            return [t for t in self.record.metadata.get_element('.//{0}type'.format(dc), delimiter=';')]
        except TypeError:
            return None


class QDC_Record(DC_Record):

    def __init__(self, record):
        """
        Qualified Dublin Core record class. Element text is available through self.element properties. Subclass of citrus.DC_Record
        :param record: oai_qdc record
        """
        DC_Record.__init__(self, record)

    @property
    def abstract(self):
        try:
            return [abstract for abstract in self.record.metadata.get_element('.//{0}abstract'.format(dcterms))]
        except TypeError:
            return None

    @property
    def alternative(self):
        try:
            return [alt for alt in self.record.metadata.get_element('.//{0}alternative'.format(dcterms))]
        except TypeError:
            return None

    @property
    def is_part_of(self):
        try:
            return [alt for alt in self.record.metadata.get_element('.//{0}isPartOf'.format(dcterms))]
        except TypeError:
            return None

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
            return None

    @property
    def place(self):
        try:
            return [{'name': place} for place in
                    self.record.metadata.get_element('.//{0}spatial'.format(dcterms), delimiter=';')]
        except TypeError:
            return None


class MODS_Record(CitrusRecord):

    def __init__(self, record):
        """
        MODS record class making MAPv4 elements available through self.element properties
        :param record: OAI-PMH MODS record
        """
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
