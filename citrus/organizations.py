class DataProvider(object):

    __slots__ = ('__dict__', 'key', 'scenario', 'map', 'data_provider', 'intermediate_provider')

    def __init__(self):
        """
        DataProvider object model.
        __slots__:
            * key: Unique string identifying organization providing the data
            * scenario: citrus.scenario class used to encapsulate records
            * map: Name of function used to map records from OAI-PMH into MAPv4. Can come from citrus.maps or be defined elsewhere
            * thumbnail: dict of information needed to create thumbnail (dpla.preview) link
                * name: Identifies which path to take in citrus.assets.thumbnail method
                * prefix: Either a url prefix or OAI-PMH record used to generate thumbnail url path
            * data_provider: Name of organization providing the data (dpla.dataProvider)
            * intermediate_provider: Name of organization serving as an intermediary data provider (dpla.intermediateProvider) -- optional
        """
        object.__init__(self)
