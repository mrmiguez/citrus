import unittest
import json  # test

from os.path import abspath, dirname, join
from citrus import FlaLD_DC, FlaLD_MODS, FlaLD_QDC
from custom_mods import FlMem

PATH = abspath(dirname(__file__))


class FlMemTests(unittest.TestCase):

    def setUp(self):
        self.dc_json = FlMem(join(PATH, 'debug/test_data/FlMemSmall.xml'),
                           tn={'name': 'web-scrape', 'prefix': 'https://www.floridamemory.com'},
                           dprovide='University of Miami-TEMP')  # TODO

    def test_dc_SourceResourceCollection(self):
        expected = [{'name': 'State Archives of Florida, M87-20'},
                    {'name': 'State Archives of Florida, M87-20'},
                    {'name': 'State Archives of Florida, S49'}]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['collection']
                                      for record in self.dc_json]))

    def test_dc_SourceResourceCreator(self):
        expected = [[{'name': 'McNeill, Martha'}],
                    [{'name': 'Putnam, Benjamin A.'},
                     {'name': 'Gibbs, Kingsley B.'},
                     {'name': 'Kingsley, George'}],
                    [{'name': 'Kingsley, Zephaniah (1765-1843)'}]]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['creator']
                                      for record in self.dc_json]))

    def test_dc_SourceResourceContributor(self):
        expected = [[{'name': 'Buckethead'}],
                    [{'name': 'Primus'}],
                    [{'name': 'Thee Oh Sees'}]]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['contributor']
                                      for record in self.dc_json]))

    def test_dc_SourceResourceDate(self):
        expected = [{'begin': '1844-10-28', 'end': '1844-10-28', 'displayDate': '1844-10-28'},
                    {'begin': '1846-09-05', 'end': '1846-09-05', 'displayDate': '1846-09-05'},
                    {'begin': '1843-07-20', 'end': '1843-07-20', 'displayDate': '1843-07-20'}]
        results = []
        for record in self.dc_json:
            if 'date' in record['sourceResource'].keys():
                results.append(record['sourceResource']['date'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceDescription(self):
        expected = [['The petition to the will made by Martha McNeill and others to Judge Farquhar Bethune, filed November 30, 1844.'],
                    ['The executor\'s response (Benjamin A. Putnam and Kingsley B. Gibbs) to the petition of Anna M. J. Kingsley, widow of Zephaniah Kingsley. September 5, 1846.'],
                    ['A handwritten copy of the will of Zephaniah Kingsley from the 1886 Supreme Court case files.']]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['description'])
        self.assertEqual(sorted(expected), sorted(results))

    def test_dc_SourceResourceIdentifier(self):
        expected = ['oai:www.floridamemory.com:177999',
                    'oai:www.floridamemory.com:178002',
                    'oai:www.floridamemory.com:178006']
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['identifier'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceLanguage(self):
        expected = [[{"name": "English", "iso_639_3": "eng"}],
                    [{"name": "Spanish", "iso_639_3": "spa"}],
                    [{"name": "German", "iso_639_3": "ger"}]]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['language'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourcePublisher(self):
        expected = ['IDW']
        results = []
        for record in self.dc_json:
            if 'publisher' in record['sourceResource'].keys():
                results.append(record['sourceResource']['publisher'][0])
        self.assertTrue(all(x in results for x in expected))

    # def test_dc_SourceResourceRights(self):
    #     expected = [[{'text': 'Rights 4A'}],
    #                 [{'text': 'Rights E3'}],
    #                 [{'text': 'Rights 1C'}]]
    #     results = []
    #     for record in self.dc_json:
    #         results.append(record['sourceResource']['rights'])
    #     self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceSubject(self):
        expected = [[{"name": "Interracial marriage--Law and legislation--United States--History--19th century"}],
                    [{"name": "Interracial marriage--Law and legislation--United States--History--19th century"}],
                    [{"name": "Interracial marriage--Law and legislation--United States--History--19th century"},
                     {"name": "Slaveholders--Florida--History"}, {"name": "Slaves -- United States -- Social conditions"}]]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['subject'])
        self.assertTrue(all(x in results for x in expected))

    # def test_dc_SourceResourceSpatial(self):
    #     expected = [[{'name': 'Moon'}],
    #                 [{'name': 'Homestead (Fla.)'}],
    #                 [{'name': 'Mars'}, {'name': 'n-dimensional space'}]]
    #     results = []
    #     for record in self.dc_json:
    #         results.append(record['sourceResource']['spatial'])
    #     self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceTitle(self):
        expected = ['Will of Zephaniah Kingsley',
                    'Executors\' response to the petition of Anna M. J. Kingsley',
                    'Petition to the will of Zephaniah Kingsley']
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['title'][0])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceTemporal(self):
        expected = ['Florida Territorial Period (1822-1845).',
                    'Florida Territorial Period (1822-1845).',
                    'Florida Territorial Period (1822-1845).']
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['temporal'][0])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceType(self):
        expected = [['Kingsley Paper', 'text', 'petitions'],
                    ['Kingsley Paper', 'text', 'decisions '],
                    ['Kingsley Paper', 'text', 'wills']]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['type'])
        self.assertTrue(all(x in results for x in expected))

    #   def test_dc_AggregationDataProvider(self):

    def test_dc_AggregationIsShownAt(self):
        expected = ['http://www.floridamemory.com/items/show/177999',
                    'http://www.floridamemory.com/items/show/178002',
                    'http://www.floridamemory.com/items/show/178006']
        results = []
        for record in self.dc_json:
            results.append(record['isShownAt'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_AggregationPreview(self):
        expected = ['https://www.floridamemory.com/fpc/memory/Collections/kingsley/images/petition/1_.jpg',
                    'https://www.floridamemory.com/fpc/memory/Collections/kingsley/images/response/1_.jpg',
                    'https://www.floridamemory.com/fpc/memory/Collections/kingsley/images/will/1_.jpg']
        results = []
        for record in self.dc_json:
            results.append(record['preview'])
        self.assertTrue(all(x in results for x in expected))

    # #   def test_dc_AggregationProvider(self):


class DCTests(unittest.TestCase):
    """

    """
    def setUp(self):
        self.dc_json = FlaLD_DC(join(PATH, 'debug/test_data/DCdebugSmall.xml'),
                           tn={'name': 'custom_field', 'prefix': 'http://dpanther.fiu.edu/sobek/content'},
                           dprovide='University of Miami-TEMP')

    def test_dc_SourceResourceCreator(self):
        expected = [[{'name': 'Alexander Hamilton'}],
                    [{'name': 'Karl Cassell'}],
                    [{'name': 'Lewis Carroll'}]]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['creator']
                                      for record in self.dc_json]))

    def test_dc_SourceResourceContributor(self):
        expected = [[{'name': 'Buckethead'}],
                    [{'name': 'Primus'}],
                    [{'name': 'Thee Oh Sees'}]]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['contributor']
                                      for record in self.dc_json]))

    def test_dc_SourceResourceDate(self):
        expected = [{'begin': '1974', 'end': '1974', 'displayDate': '1974'},
                    {'begin': '1972', 'end': '1972', 'displayDate': '1972'}]
        results = []
        for record in self.dc_json:
            if 'date' in record['sourceResource'].keys():
                results.append(record['sourceResource']['date'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceDescription(self):
        expected = [['1 postcard, postally unused', 'caption: "Tropical Scenes, South of Florida, U.S.A.", "Copyright 1891 by Geo. Barker."'],
                    ['1 postcard, postally used', 'caption: "View from highway, Royal Palm State Park, Homestead, Florida".',
                     '"The Park Contains 4000 Acres:–960 acres ceded by the State of Florida in 1915, 960 acres donated by Mrs. Henry M. Flagler, and 2080 acres ceded by the State of Florida in 1921. Trails provide access to the beauties and marvels of the tropical forest".'],
                    ['1 postcard, postally unused', 'caption: "Alligator Joe watching the Young Alligators Hatch."']]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['description'])
        self.assertEqual(sorted(expected), sorted(results))

    def test_dc_SourceResourceIdentifier(self):
        expected = ['http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07050832/00001',
                    'http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07050842/00001',
                    'http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07040407/00001']
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['identifier'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceLanguage(self):
        expected = [{"name": "English"},
                    {"name": "English"},
                    {"name": "English"}]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['language'][0])
        self.assertTrue(all(x in results for x in expected))

#    def test_dc_SourceResourcePublisher(self):
#        """"""
#        pass

    def test_dc_SourceResourceRights(self):
        expected = [[{'text': 'Rights 4A'}],
                    [{'text': 'Rights E3'}],
                    [{'text': 'Rights 1C'}]]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['rights'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceSubject(self):
        expected = [[{"name": "Alligators--Florida--Everglades."}],
                    [{"name": "Homestead (Fla.)"}, {"name": "Everglades (Fla.)"}],
                    [{"name": "Tropical forests"}, {"name": "Everglades (Fla.)"}]]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['subject'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceSpatial(self):
        expected = [[{'name': 'Moon'}],
                    [{'name': 'Homestead (Fla.)'}],
                    [{'name': 'Mars'}, {'name': 'n-dimensional space'}]]
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['spatial'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_SourceResourceTitle(self):
        expected = ['Alligator Joe watching the young alligators hatch',
                    'View from highway, Royal Palm State Park, Homestead, Florida',
                    'Tropical Scenes, South of Florida, U.S.A.']
        results = []
        for record in self.dc_json:
            results.append(record['sourceResource']['title'][0])
        self.assertTrue(all(x in results for x in expected))

#   def test_dc_AggregationDataProvider(self):

    def test_dc_AggregationIsShownAt(self):
        expected = ['http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07050832/00001',
                    'http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07050842/00001',
                    'http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07040407/00001']
        results = []
        for record in self.dc_json:
            results.append(record['isShownAt'])
        self.assertTrue(all(x in results for x in expected))

    def test_dc_AggregationPreview(self):
        expected = ['http://dpanther.fiu.edu/sobek/content/FI/07/05/08/32/00001/FI07050832_001thm.jpg',
                    'http://dpanther.fiu.edu/sobek/content/FI/07/05/08/42/00001/FI07050842_001thm.jpg',
                    'http://dpanther.fiu.edu/sobek/content/FI/07/04/04/07/00001/FI07040407_001thm.jpg']
        results = []
        for record in self.dc_json:
            results.append(record['preview'])
        self.assertTrue(all(x in results for x in expected))

#   def test_dc_AggregationProvider(self):


class QDCTests(unittest.TestCase):
    """

    """
    def setUp(self):
        self.qdc_json = FlaLD_QDC(join(PATH, 'debug/test_data/QDCdebugSmall.xml'),
                             tn={'name':'cdm', 'prefix': 'http://merrick.library.miami.edu'},
                             dprovide='University of Miami-TEMP')

    def test_qdc_SourceResourceCreator(self):
        expected = [[{'name': 'Gilpin, Vincent'}],
                    [{'name': 'Munroe, Jessie N.'}],
                    [{'name': 'Thurston Moore'}]]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['creator']
                                      for record in self.qdc_json]))

    def test_qdc_SourceResourceContributor(self):
        expected = [[{'name': 'Buckethead'}],
                    [{'name': 'Primus'}, {'name': 'Jurassic 5'}],
                    [{'name': 'Thee Oh Sees'}]]
        self.assertTrue(all(x in expected
                            for x in [record['sourceResource']['contributor']
                                      for record in self.qdc_json]))

    def test_qdc_SourceResourceDate(self):
        expected = [{'begin': '1933-09-03', 'end': '1933-09-03', 'displayDate': '1933-09-03'},
                    {'begin': '1915-04-26', 'end': '1915-04-26', 'displayDate': '1915-04-26'},
                    {'begin': '1912-01-16', 'end': '1912-01-16', 'displayDate': '1912-01-16'}]
        results = []
        for record in self.qdc_json:
            if 'date' in record['sourceResource'].keys():
                results.append(record['sourceResource']['date'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceDescription(self):
        expected = [['Test 001', 'Test 000'],
                    ['Test 002', 'Test 003']]
        results = []
        for record in self.qdc_json:
            if 'description' in record['sourceResource'].keys():
                results.append(record['sourceResource']['description'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceExtent(self):
        expected = [['1 letter'],
                    ['2 letters'],
                    ['4 letters']]
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['extent'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceGenre(self):
        expected = [[{'name': 'Photographs'}]]
        results = []
        for record in self.qdc_json:
            if 'genre' in record['sourceResource'].keys():
                results.append(record['sourceResource']['genre'])
        self.assertTrue(all(x in results for x in expected))


    def test_qdc_SourceResourceIdentifier(self):
        expected = ['oai:lib.fsu.edu.umiami:oai:uofm.library.umiami:oai:merrick.library.miami.edu:asm0447/31',
                    'oai:lib.fsu.edu.umiami:oai:uofm.library.umiami:oai:merrick.library.miami.edu:asm0447/39',
                    'oai:lib.fsu.edu.umiami:oai:uofm.library.umiami:oai:merrick.library.miami.edu:asm0447/25']
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['identifier'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceLanguage(self):
        expected = [{"iso_639_3": "eng"},
                    {"iso_639_3": "eng"},
                    {"iso_639_3": "eng"}]
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['language'][0])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourcePublisher(self):
        expected = [['IDW'],
                    ['Image Comics'],
                    ['Arista Records']]
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['publisher'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceRights(self):
        expected = [[{'@id': 'http://rightsstatements.org/page/UND/1.0/'}],
                    [{'text': 'Rights E3'}],
                    [{'@id': 'http://rightsstatements.org/vocab/InC/1.0/'}]]
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['rights'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceSubject(self):
        expected = [[{"name": "Gilpin, Vincent"}, {"name": "Munroe, Patty"}, {"name": "Munroe, Ralph, 1851-1933"}, {"name": "Letters"}],
                    [{"name": "Letters"}],
                    [{"name": "Munroe, Patty"}, {"name": "Letters"}]]
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['subject'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceSpatial(self):
        expected = [[{'name': 'Coconut Grove (Miami, Fla.)'},
                     {'name': 'Canterbury'}, {'name': 'Outside'}],
                    [{'name': 'Death Star'}],
                    [{'name': 'Excelsior (Minn.)'}]]
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['spatial'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceTitle(self):
        expected = ['Vincent Gilpin letter to Patty Munroe, September 3, 1933',
                    'Jessie N. Munroe letter to Mrs. Gilpin, January 16, 1912',
                    'Jessie N. Munroe letter to Mrs. Gilpin, April 26, 1915']
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['title'][0])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_SourceResourceType(self):
        expected = ['Text',
                    'Rebel Alliance Victory Plans',
                    'Tax return from a VIP']
        results = []
        for record in self.qdc_json:
            results.append(record['sourceResource']['type'][0])
        self.assertTrue(all(x in results for x in expected))

#   def test_qdc_AggregationDataProvider(self):

    def test_qdc_AggregationIsShownAt(self):
        expected = ['http://merrick.library.miami.edu/cdm/ref/collection/asm0447/id/31',
                    'http://merrick.library.miami.edu/cdm/ref/collection/asm0447/id/39',
                    'http://merrick.library.miami.edu/cdm/ref/collection/asm0447/id/25']
        results = []
        for record in self.qdc_json:
            results.append(record['isShownAt'])
        self.assertTrue(all(x in results for x in expected))

    def test_qdc_AggregationPreview(self):
        expected = ['http://merrick.library.miami.edu/utils/getthumbnail/collection/asm0447/id/31',
                    'http://merrick.library.miami.edu/utils/getthumbnail/collection/asm0447/id/39',
                    'http://merrick.library.miami.edu/utils/getthumbnail/collection/asm0447/id/25']
        results = []
        for record in self.qdc_json:
            results.append(record['preview'])
        self.assertTrue(all(x in results for x in expected))

#   def test_qdc_AggregationProvider(self):


class MODSTests(unittest.TestCase):
    """

    """
    def setUp(self):
        self.mods_json = FlaLD_MODS(join(PATH, 'debug/test_data/MODSdebugSmall.xml'),
                               tn={'name': 'islandora', 'prefix': 'http://fsu.digital.flvc.org/islandora/object'},
                               dprovide='Florida State University Libraries')

    def test_mods_SourceResourceAlternative(self):
        expected = [['Test 06']]
        results = []
        for record in self.mods_json:
            if 'alternative' in record['sourceResource'].keys():
                results.append(record['sourceResource']['alternative'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceCollection(self):
        expected = [{'_:id': 'http://purl.fcla.edu/fsu/MSS_2015-007', 'name': 'Davis Houck Papers, 1955 - 2006'},
                    {'_:id': 'Test 04', 'name': 'Test 05'}]
        results = []
        for record in self.mods_json:
            if 'collection' in record['sourceResource'].keys():
                results.append(record['sourceResource']['collection'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceCreator(self):
        expected = [[{'name': 'Mauldin, Bob'}], [{'name': 'Mittan, J. Barry'}]]
        results = []
        for record in self.mods_json:
            if 'creator' in record['sourceResource'].keys():
                results.append(record['sourceResource']['creator'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceContributor(self):
        expected = [[{'name': 'Miguez, Matthew Roland'}],
                    [{'name': 'Houck, Davis W.', '@id': 'http://id.loc.gov/authorities/names/n91016636'}]]
        results = []
        for record in self.mods_json:
            if 'contributor' in record['sourceResource'].keys():
                results.append(record['sourceResource']['contributor'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceDate(self):
        expected = [{'begin': '2013-05-27', 'end': '2013-05-27', 'displayDate': '2013-05-27'},
                    {'begin': 'circa 1965-1971', 'end': 'circa 1965-1971', 'displayDate': 'circa 1965-1971'},
                    {'begin': '1935', 'end': '1969', 'displayDate': '1935 - 1969'}]
        results = []
        for record in self.mods_json:
            if 'date' in record['sourceResource'].keys():
                results.append(record['sourceResource']['date'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceDescription(self):
        expected = [['Test 00'], ['Test 03']]
        results = []
        for record in self.mods_json:
            if 'description' in record['sourceResource'].keys():
                results.append(record['sourceResource']['description'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceExtent(self):
        expected = [['3 MB'], ['8 x 10 in.']]
        results = []
        for record in self.mods_json:
            if 'extent' in record['sourceResource'].keys():
                results.append(record['sourceResource']['extent'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceGenre(self):
        expected = [[{"name": "Photographs"}], [{"name": "Photographic prints", "@id": "http://id.loc.gov/vocabulary/graphicMaterials/tgm007718"}]]
        results = []
        for record in self.mods_json:
            if 'genre' in record['sourceResource'].keys():
                results.append(record['sourceResource']['genre'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceIdentifier(self):
        expected = ['http://purl.flvc.org/fsu/fd/FSU_MSS_2015-007_S03_SS02_I003',
                    'http://purl.flvc.org/fcla/dt/107201',
                    'http://purl.flvc.org/fsu/fd/FSUspcn329b']
        results = []
        for record in self.mods_json:
            results.append(record['sourceResource']['identifier'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceLanguage(self):
        expected = [[{"name": "English", "iso_639_3": "eng"}]]
        results = []
        for record in self.mods_json:
            if 'language' in record['sourceResource'].keys():
                results.append(record['sourceResource']['language'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourcePublisher(self):
        expected = [['Heritage Protocol, Florida State University, Tallahassee, Florida.']]
        results = []
        for record in self.mods_json:
            if 'publisher' in record['sourceResource'].keys():
                results.append(record['sourceResource']['publisher'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceRights(self):
        expected = [[{"@id": 'http://rightsstatements.org/vocab/NoC-US/1.0/'}],
                    [{"text": 'Rights AB'},
                    {"text": 'Rights AC'}],  # these two actually shouldn't appear... check after pymods==1.0.0 switch
                    [{"text": 'WHAT A BUG!'}]]  # TODO investigate comment above
        results = []
        for record in self.mods_json:
            results.append(record['sourceResource']['rights'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceSubject(self):
        expected = [[{"name": "Students"}, {"name": "Greek life"}, {"name": "Fraternities and Sororities"}],
                    [{"name": "Florida State University"}, {"name": "Photography"},
                     {"name": "Mittan, J. Barry"}, {"name": "Karate"},
                     {"name": "Student Life"}, {"name": "Journalism"},
                     {"name": "circa 1960s"}, {"name": "Campus Scenes"}],
                    [{"@id": "http://id.loc.gov/authorities/subjects/sh2007100199",
                      "name": "African Americans--Civil rights--History--20th century"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh85001942",
                      "name": "African Americans--Crimes against"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh85026371",
                      "name": "Civil rights"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh2008106179",
                      "name": "Journalism--Political aspects--United States"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh2008115909",
                      "name": "Mississippi--Race relations"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh90002616",
                      "name": "Racism in the press"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh2008110371",
                      "name": "Rhetoric--Political aspects--United States--History--20th century"},
                     {"@id": "http://id.loc.gov/authorities/subjects/sh2010117082",
                      "name": "Trials (Murder)--United States"}]]
        results = []
        for record in self.mods_json:
            results.append(record['sourceResource']['subject'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceSpatial(self):
        expected = [[{"lat": "32.712", "long": "-89.653", "name": "Mississippi",
                      "_:attribution": "This record contains information from Thesaurus of Geographic Names (TGN) which is made available under the ODC Attribution License."}]]
        results = []
        for record in self.mods_json:
            if 'spatial' in record['sourceResource'].keys():
                results.append(record['sourceResource']['spatial'])
        self.assertEqual(results, expected)

    def test_mods_SourceResourceTitle(self):
        expected = ['Fraternity fundraiser for injured student',
                    'Student Life Contact Sheet',
                    'Drew Shed: A Shed Alone']
        results = []
        for record in self.mods_json:
            results.append(record['sourceResource']['title'][0])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_SourceResourceType(self):
        expected = ['still image',
                    'moving image']
        results = []
        for record in self.mods_json:
            results.append(record['sourceResource']['type'])
        self.assertTrue(all(x in results for x in expected))

#    def test_mods_AggregationDataProvider(self):

    def test_mods_AggregationIsShownAt(self):
        expected = ['http://purl.flvc.org/fsu/fd/FSUspcn329b',
                    'http://purl.flvc.org/fcla/dt/107201',
                    'http://purl.flvc.org/fsu/fd/FSU_MSS_2015-007_S03_SS02_I003']
        results = []
        for record in self.mods_json:
            results.append(record['isShownAt'])
        self.assertTrue(all(x in results for x in expected))

    def test_mods_AggregationPreview(self):
        expected = ['http://fsu.digital.flvc.org/islandora/object/fsu:24694/datastream/TN/view',
                    'http://fsu.digital.flvc.org/islandora/object/fsu:9420/datastream/TN/view',
                    'http://fsu.digital.flvc.org/islandora/object/fsu:394576/datastream/TN/view']
        results = []
        for record in self.mods_json:
            results.append(record['preview'])
        self.assertTrue(all(x in results for x in expected))

#    def test_mods_AggregationProvider(self):

if __name__ == '__main__':
    unittest.main()