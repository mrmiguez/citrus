"""
Source document parsers and record classes for returning XML or JSON document values
"""
import re
import requests
import json

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


class SSDNPartnerMODSScenario(SSDNMODS):

    def __init__(self, xml_path):
        """
        :param xml_path: Path to an XML file of OAI-PMH MODS records
        """
        SSDNMODS.__init__(self, xml_path)
        self.records = [SSDNMODSRecord(record) for record in self.records]


class APIScenario(Scenario):

    def __init__(self, url, record_key, count_key=None, page_key=None):
        r = requests.get(url)
        data = json.loads(r.text.replace('\\u00a0', ''))
        if count_key:
            record_count = [v for v in self._item_generator(data, count_key)][0]
        self.records = [record for record in self._item_generator(data, record_key)]
        if record_count:
            page = 1
            while len(self.records) < record_count:
                page += 1
                data = json.loads(requests.get(url + f'&{page_key}={page}').text.replace('\\u00a0', ''))
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
        self.ns = '{http://purl.org/dc/elements/1.1/}'

    def _value_list(self, elem, ns):
        try:
            return [value.strip(':').strip(' ') for value in
                    self.record.metadata.get_element('.//{0}{1}'.format(ns, elem), delimiter=';')
                    if value]
        except TypeError:
            return None

    @property
    def contributor(self):
        return self._value_list('contributor', dc)

    @property
    def creator(self):
        return self._value_list('creator', dc)

    @property
    def date(self):
        return self._value_list('date', dc)

    @property
    def description(self):
        return self._value_list('description', dc)
    @property
    def format(self):
        return self._value_list('format', dc)

    @property
    def identifier(self):
        return self._value_list('identifier', dc)

    @property
    def language(self):
        return self._value_list('language', dc)

    @property
    def place(self):
        return self._value_list('coverage', dc)

    @property
    def publisher(self):
        return self._value_list('publisher', dc)

    @property
    def rights(self):
        return self._value_list('rights', dc)

    @property
    def subject(self):
        try:
            return [re.sub("\( lcsh \)$", '', sub).strip(' ') for sub in
                    self.record.metadata.get_element('.//{0}subject'.format(dc), delimiter=';') if sub]
        except TypeError:
            return None

    @property
    def title(self):
        return self._value_list('title', dc)

    @property
    def thumbnail(self):
        try:
            return self.record.metadata.get_element('.//{0}identifier.thumbnail'.format(dc))[0]
        except TypeError:
            return None

    @property
    def type(self):
        return self._value_list('type', dc)


class QDCRecord(DCRecord):

    def __init__(self, record):
        """
        Qualified Dublin Core record class. Element text is available through self.element properties. Subclass of citrus.DC_Record
        :param record: oai_qdc record
        """
        DCRecord.__init__(self, record)

    @property
    def abstract(self):
        return self._value_list('abstract', dcterms)

    @property
    def alternative(self):
        return self._value_list('alternative', dcterms)

    @property
    def is_part_of(self):
        return self._value_list('isPartOf', dcterms)

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
        return self._value_list('extent', dcterms)

    @property
    def medium(self):
        return self._value_list('medium', dcterms)

    @property
    def place(self):
        return self._value_list('spatial', dcterms)

    @property
    def requires(self):
        return self._value_list('requires', dcterms)


class MODSRecord(XMLRecord):

    def __init__(self, record):
        """
        MODS record class making MAPv4 elements available through self.element properties
        :param record: OAI-PMH MODS record
        """
        XMLRecord.__init__(self, record)
        self.oai_urn = self.record.oai_urn
        self.metadata = self.record.metadata

    @property
    def alternative(self):
        return self.record.metadata.titles[1:]

    @property
    def collection(self):
        try:
            return self.record.metadata.collection
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
    def geographic_code(self):
        return self.record.metadata.geographic_code

    @property
    def identifier(self):
        return self.record.metadata.purl[0]

    @property
    def iid(self):
        return self.record.metadata.iid

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
    def pid(self):
        if self.record.metadata.pid:
            return self.record.metadata.pid
        else:
            return self.record.oai_urn.split(':')[-1].replace('_', ':')

    @property
    def publisher(self):
        return self.record.metadata.publisher

    # sourceResource.relation

    # sourceResource.isReplacedBy

    # sourceResource.replaces

    @property
    def rights(self):
        for rights in self.record.metadata.rights:
            if rights.uri:
                return rights.uri
            else:
                return rights.text

    @property
    def subject(self):
        return [{"@id": subject.uri, "name": subject.text}
                if subject.uri
                else {"name": subject.text}
                for subject in self.record.metadata.subjects if
                'eographic' not in subject.elem.tag]

    @property
    def title(self):
        return self.record.metadata.titles[0]

    @property
    def type(self):
        return self.record.metadata.type_of_resource


class SSDNMODSRecord(MODSRecord):

    def __init__(self, record):
        MODSRecord.__init__(self, record)

    @property
    def creator(self):
        # Case 1: Name has either role.text=Creator or role.code=cre
        # Case 2: Name has incorrectly formed role.text=creator
        # Case 3: Name has neither role.text nor role.code
        names = self.record.metadata.get_creators + self.record.metadata.get_names(
            role="creator") + self.record.metadata.get_names(role=None)
        return [{"@id": name.uri, "name": name.text} if name.uri else {"name": name.text} for name in
                names]

    @property
    def rights(self):
        # TODO: this is real ugly and will break if there are no RS.org URIs to return
        for rights in self.record.metadata.rights:
            if rights.uri:
                return rights.uri
            else:
                if rights.text.startswith('http'):
                    return rights.text
                else:
                    continue


class InternetArchiveRecord(CitrusRecord):

    def __init__(self, record):
        CitrusRecord.__init__(self, record)
        self.harvest_id = f'ia:{self.identifier}'

    @property
    def identifier(self):
        return self.record['identifier']

    def __getattr__(self, item):
        return self.record[item]
