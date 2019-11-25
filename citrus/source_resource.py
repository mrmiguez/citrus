import json


class SourceResource(object):
    #__slots__ = ('alternative_title', 'collection', 'contributor', 'creator', 'date', 'description', 'extent',
    #             'format', 'genre', 'identifier', 'language', 'place', 'publisher', 'relation', 'replaced_by',
    #             'replaces', 'rights', 'rights_holder', 'subject', 'temporal_coverage', 'title', 'type')

    def __init__(self):
        """

        """
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
