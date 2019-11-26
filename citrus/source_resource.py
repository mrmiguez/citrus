import json


class SourceResource(object):

    def __init__(self):
        """

        """
        object.__init__(self)

    def __setattr__(self, key, value):
        if value is not None:
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
