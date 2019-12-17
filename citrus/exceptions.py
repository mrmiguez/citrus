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
