class CitrusException(Exception):
    pass


class ScenarioException(CitrusException):
    """

    """


class SSDN_QDCException(ScenarioException, TypeError):

    def __init__(self, msg):
        TypeError.__init__(self, msg)
        self.msg = msg
