class CitrusException(Exception):
    pass


class ScenarioException(CitrusException):
    """

    """


class SSDN_QDCException(ScenarioException, TypeError):

    def __init__(self, msg):
        TypeError.__init__(self, msg)
        self.msg = msg


class SourceResourceException(CitrusException):

    def __init__(self, msg):
        CitrusException.__init__(self, msg)
        self.msg = msg


class SourceResourceRequiredElementException(SourceResourceException):

    def __init__(self, record, elem):
        SourceResourceException.__init__(self, f"Required element {elem} is None: {record}")


class CitrusProfileError(CitrusException, KeyError):

    def __init__(self, profile, config_file):
        self.msg = f'Profile: {profile} is not listed in {config_file}'
        KeyError.__init__(self, self.msg)


class RecordGroupFileExtensionError(CitrusException, ValueError):

    def __init__(self, fp):
        self.msg = f'File: {fp} does not have a supported file extension (.json or .jsonl)'
        ValueError.__init__(self, self.msg)
