import json
from datetime import date
from os.path import exists, join
from citrus.exceptions import SourceResourceRequiredElementException


class Record(object):

    def __init__(self):
        """
        Generic object class. Provides some JSON-like methods
        """
        object.__init__(self)

    def __setattr__(self, key, value):
        if value:
            self.__dict__[key] = value

    def __str__(self):
        try:
            return f'{self.__class__.__name__}, {self.__dict__["identifier"]}'
        except KeyError:
            return f'{self.__repr__()}'

    def dumps(self, indent=None):
        return json.dumps(self.__dict__, indent=indent)

    @property
    def data(self):
        return self.__dict__


class DPLARecord(Record):

    def __init__(self):
        """
        DPLA MAPv4 record class. Serves as the JSON-LD wrapper for citrus.SourceResource. Includes some default attributes for convenience.
        """
        Record.__init__(self)
        self.__dict__['@context'] = "http://api.dp.la/items/context"
        self.provider = {"name": "Sunshine State Digital Network"}
        self.aggregatedCHO = "#sourceResource"


class SourceResource(Record):

    def __init__(self):
        """
        DPLA MAPv4 sourceResource record class
        """
        Record.__init__(self)

    def __setattr__(self, key, value):
        if key == 'rights' and not value:
            raise SourceResourceRequiredElementException(self, 'Rights')
        elif key == 'title' and not value:
            raise SourceResourceRequiredElementException(self, 'Title')
        elif value:
            self.__dict__[key] = value


class RecordGroup(object):

    def __init__(self, records=None):
        """

        :param records:
        """
        object.__init__(self)
        if records:
            self.records = self.records + [rec for rec in records]
        else:
            self.records = []

    def append(self, record):
        self.records.append(record)

    def load(self, fp):
        return NotImplemented

    def write_json(self, fp, prefix=None, pretty_print=False):
        """

        :param fp:
        :param prefix:
        :param pretty_print:
        :return:
        """
        if prefix:
            f = f'{prefix}-{date.today()}'
        else:
            f = f'{date.today()}'
        if exists(join(fp, f'{f}.json')):
            with open(join(fp, f'{f}.json'), 'r', encoding='utf-8') as json_in:
                data = json.load(json_in)
                for record in data:
                    self.records.append(record)
            with open(join(fp, f'{f}.json'), 'w', encoding='utf-8') as json_out:
                if pretty_print:
                    json.dump(self.records, json_out, indent=2)
                else:
                    json.dump(self.records, json_out)
        else:
            with open(join(fp, f'{f}.json'), 'w', encoding='utf-8') as json_out:
                if pretty_print:
                    json.dump(self.records, json_out, indent=2)
                else:
                    json.dump(self.records, json_out)

    def write_jsonl(self, fp, prefix=None):
        """

        :param fp:
        :param prefix:
        :return:
        """
        if prefix:
            f = f'{prefix}-{date.today()}'
        else:
            f = f'{date.today()}'
        with open(join(fp, f'{f}.jsonl'), 'a', encoding='utf-8', newline='\n') as json_out:
            for rec in self.records:
                json_out.write(json.dumps(rec) + '\n')

    def print(self):
        for rec in self.records:
            print(json.dumps(rec))



def dedupe_record_group():
    pass

