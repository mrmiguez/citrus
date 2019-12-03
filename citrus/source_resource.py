import json
from citrus.exceptions import SourceResourceRequiredElementException


class Record(object):

    def __init__(self):
        object.__init__(self)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

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
