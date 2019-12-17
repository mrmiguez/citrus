import json
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

    def write_json(self):
        """

        :return:
        """
        raise NotImplementedError

    def write_jsonl(self):
        """

        :return:
        """
        raise NotImplementedError

    def dumps(self, indent=None):
        return json.dumps(self.__dict__, indent=indent)


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

    @property
    def data(self):
        return self.__dict__
