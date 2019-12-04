import json
from citrus.exceptions import SourceResourceRequiredElementException


class Record(object):

    def __init__(self):
        object.__init__(self)

    def __setattr__(self, key, value):
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

    def write_jsonl(self):
        """

        :return:
        """

    def dumps(self, indent=None):
        return json.dumps(self.__dict__, indent=indent)


class SourceResource(Record):

    def __init__(self):
        """

        """
        Record.__init__(self)

    def __setattr__(self, key, value):
        if key == 'rights' and not value:
            raise SourceResourceRequiredElementException('Rights')
        elif key == 'title' and not value:
            raise SourceResourceRequiredElementException('Title')
        elif value:
            self.__dict__[key] = value

    @property
    def data(self):
        return self.__dict__
