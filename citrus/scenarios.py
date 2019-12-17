from pymods import OAIReader

dc = '{http://purl.org/dc/elements/1.1/}'
dcterms = '{http://purl.org/dc/terms/}'


class Scenario:

    def __init__(self, records):
        self.records = records

    def __getitem__(self, item):
        return self.records[item]

    def __iter__(self):
        for record in self.records:
            yield record

    def __len__(self):
        return len(self.records)

    def __str__(self):
        return f'{self.__class__.__name__}'


class XMLScenario(Scenario):

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
        Scenario.__init__(self, self.records)


class SSDNDC(XMLScenario):

    def __init__(self, xml_path):
        """
        Parser and container for citrus.DC_Record records
        :param xml_path: Path to an XML file of oai_dc records
        """
        XMLScenario.__init__(self, xml_path)
        self.records = [DCRecord(record) for record in self.records]


class SSDNQDC(XMLScenario):

    def __init__(self, xml_path):
        """
        Parser and container for citrus.QDC_Record records
        :param xml_path: Path to an XML file of oai_qdc records
        """
        XMLScenario.__init__(self, xml_path)
        self.records = [QDCRecord(record) for record in self.records]


class SSDNMODS(XMLScenario):

    def __init__(self, xml_path):
        """
        Parser and container for citrus.MODS_Record records
        :param xml_path: Path to an XML file of OAI-PMH MODS records
        """
        XMLScenario.__init__(self, xml_path)
        self.records = [MODSRecord(record) for record in self.records]


class APIScenario(Scenario):

    def __init__(self, url, record_key, count_key=None, page_key=None):
        import requests
        import json
        r = requests.get(url)
        data = json.loads(r.text)
        if count_key:
            record_count = [v for v in self._item_generator(data, count_key)][0]
        self.records = [record for record in self._item_generator(data, record_key)]
        if record_count:
            page = 1
            while len(self.records) < record_count:
                page += 1
                data = json.loads(requests.get(url + f'&{page_key}={page}').text)
                self.records = self.records + [record for record in self._item_generator(data, record_key)]
                continue
        Scenario.__init__(self, self.records)

    def _item_generator(self, json_input, lookup_key):
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if k == lookup_key:
                    if isinstance(v, list):
                        for i in v:
                            yield i
                    else:
                        yield v
                else:
                    yield from self._item_generator(v, lookup_key)
        elif isinstance(json_input, list):
            for item in json_input:
                yield from self._item_generator(item, lookup_key)


class InternetArchive(APIScenario):

    def __init__(self, collection):
        url = f'https://archive.org/advancedsearch.php?q=collection:{collection}&output=json&rows=100'
        APIScenario.__init__(self, url, 'docs', 'numFound', 'page')
        self.records = [InternetArchiveRecord(record) for record in self.records]


class CitrusRecord:

    def __init__(self, record):
        """
        Generic class for single records
        :param record: Generic record
        """
        self.record = record

    def __str__(self):
        return f'{self.__class__.__name__}, {self.harvest_id}'


class XMLRecord(CitrusRecord):

    def __init__(self, record):
        """
        Generic class for single records. Makes record OAI-PMH identifier available through self.harvest_id attribute
        :param record: Generic record
        """
        CitrusRecord.__init__(self, record)
        self.harvest_id = self.record.oai_urn


class DCRecord(XMLRecord):

    def __init__(self, record):
        """
        Dublin Core record class. Element text is available through self.element properties
        :param record: oai_dc record
        """
        XMLRecord.__init__(self, record)

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


class QDCRecord(DCRecord):

    def __init__(self, record):
        """
        Qualified Dublin Core record class. Element text is available through self.element properties. Subclass of citrus.DC_Record
        :param record: oai_qdc record
        """
        DCRecord.__init__(self, record)

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


class MODSRecord(XMLRecord):

    def __init__(self, record):
        """
        MODS record class making MAPv4 elements available through self.element properties
        :param record: OAI-PMH MODS record
        """
        XMLRecord.__init__(self, record)

    @property
    def alternative(self):
        return self.record.metadata.titles[1:]

    @property
    def collection(self):
        try:
            return self.record.metadata.collection.title
        except (AttributeError, TypeError):
            return None

    @property
    def contributor(self):
        return [{"@id": name.uri, "name": name.text} if name.uri else {"name": name.text} for name in
                filter(self._creator_filter, self.record.metadata.names)]

    def _creator_filter(self, name):
        if name.role.text != 'Creator' and name.role.code != 'cre' and name.role.text is not None and name.role.code is not None:
            return name

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

    @property
    def rights(self):
        return [rights.text for rights in self.record.metadata.rights]

    @property
    def subject(self):
        return [{"name": subject.text} for subject in self.record.metadata.subjects if
                'eographic' not in subject.elem.tag]

    @property
    def title(self):
        return self.record.metadata.titles[0]

    @property
    def type(self):
        return self.record.metadata.type_of_resource


class InternetArchiveRecord(CitrusRecord):

    def __init__(self, record):
        CitrusRecord.__init__(self, record)
        self.harvest_id = f'ia:{self.identifier}'

    @property
    def identifier(self):
        return self.record['identifier']

    def __getattr__(self, item):
        return self.record[item]
