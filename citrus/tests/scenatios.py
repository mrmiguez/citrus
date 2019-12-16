import os
import unittest
from citrus import DataProvider

test_dir_path = os.path.abspath(os.path.dirname(__file__))


class XML_ScenarioTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import XML_Scenario
        self.scenario = XML_Scenario(os.path.join(test_dir_path, 'test_data/DCdebugSmall.xml'))

    def test_deleted_records(self):
        self.assertEqual(len(self.scenario), 3)


class CitrusRecordTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import XML_Scenario, CitrusRecord
        self.scenario = XML_Scenario(os.path.join(test_dir_path, 'test_data/DCdebugSmall.xml'))
        self.record = CitrusRecord(self.scenario.records[0])

    def test_citrus_record_oai_id(self):
        self.assertEqual(self.record.oai_id, "oai:lib.fsu.edu.fiu:oai:uofm.library.fiu:oai:dpsobek:FI07050832_00001")


class DC_RecordTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SSDN_DC
        self.scenario = SSDN_DC(os.path.join(test_dir_path, 'test_data/DCdebugSmall.xml'))
        self.record = self.scenario.records[0]

    def test_DC_record_contributor(self):
        self.assertEqual(self.record.contributor, [{'name': 'Buckethead'}])

    def test_DC_record_creator(self):
        self.assertEqual(self.record.creator, [{'name': 'Lewis Carroll'}])

    def test_DC_record_date(self):
        self.assertEqual(self.record.date, ['1974'])

    def test_DC_record_description(self):
        self.assertEqual(self.record.description, ['1 postcard, postally unused',
                                                   'caption: "Alligator Joe watching the Young Alligators Hatch."'])

    def test_DC_record_format(self):
        self.assertEqual(self.record.format, ["Embroidery"])

    def test_DC_record_identifier(self):
        self.assertEqual(self.record.identifier, ['FI07050832',
                                                  'http://dpanther.fiu.edu/dpService/dpPurlService/purl/FI07050832/00001'])

    def test_DC_record_language(self):
        self.assertEqual(self.record.language, ['English'])

    def test_DC_record_place(self):
        self.assertEqual(self.record.place, [{"name": "Moon"}])

    def test_DC_record_publisher(self):
        self.assertEqual(self.record.publisher,
                         ['Miami, Florida: J.N. Chamberlain', 'Miami, Florida: J.N. Chamberlain'])

    def test_DC_record_rights(self):
        self.assertEqual(self.record.rights, ["Rights 4A"])

    def test_DC_record_subject(self):
        self.assertEqual(self.record.subject, ['Alligators--Florida--Everglades.'])

    def test_DC_record_title(self):
        self.assertEqual(self.record.title, ["Alligator Joe watching the young alligators hatch"])

    def test_DC_record_type(self):
        self.assertEqual(self.record.type, ["Text"])


class QDC_RecordTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SSDN_QDC
        self.scenario = SSDN_QDC(os.path.join(test_dir_path, 'test_data/QDCdebugSmall.xml'))
        self.record = self.scenario.records[0]

    def test_QDC_record_abstract(self):
        self.assertEqual(self.record.abstract, ["Test 000"])

    def test_QDC_record_alternative(self):
        self.assertEqual(self.record.alternative, ["covfefe"])

    def test_QDC_record_contributor(self):
        self.assertEqual(self.record.contributor, [{'name': 'Thee Oh Sees'}])

    def test_QDC_record_creator(self):
        self.assertEqual(self.record.creator, [{'name': 'Gilpin, Vince'}])

    def test_QDC_record_date(self):
        self.assertEqual(self.record.date, ["1933-09-03"])

    def test_QDC_record_description(self):
        self.assertEqual(self.record.description, ['Test 001'])

    def test_QDC_record_extent(self):
        self.assertEqual(self.record.extent, ["1 letter"])

    def test_QDC_record_format(self):
        self.assertEqual(self.record.format, ["image/tiff"])

    def test_QDC_record_identifier(self):
        self.assertEqual(self.record.identifier, ['http://merrick.library.miami.edu/cdm/ref/collection/asm0447/id/31'])

    def test_QDC_record_language(self):
        self.assertEqual(self.record.language, ['eng'])

    def test_QDC_record_place(self):
        self.assertEqual(self.record.place, [{"name": "Excelsior (Minn.)"}])

    def test_QDC_record_publisher(self):
        self.assertEqual(self.record.publisher, ['Arista Records'])

    def test_QDC_record_rights(self):
        self.assertEqual(self.record.rights,
                         ["Rights 4A", "Copyright Undetermined http://rightsstatements.org/page/UND/1.0/"])

    def test_QDC_record_subject(self):
        self.assertEqual(self.record.subject, ['Gilpin, Vincent; Munroe, Patty; Munroe, Ralph, 1851-1933; Letters'])

    def test_QDC_record_title(self):
        self.assertEqual(self.record.title, ["Vincent Gilpin letter to Patty Munroe, September 3, 1933"])

    def test_QDC_record_type(self):
        self.assertEqual(self.record.type, ["Tax return from a VIP"])


class MODS_RecordTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SSDN_MODS
        self.scenario = SSDN_MODS(os.path.join(test_dir_path, 'test_data/MODSdebugSmall.xml'))
        self.record = self.scenario.records[0]

    def test_MODS_record_alternative(self):
        self.assertEqual(self.record.alternative, ['ALT: Fraternity fundraiser for injured student'])

    def test_MODS_record_collection(self):
        self.assertEqual(self.record.collection, 'General Jean-Jacques-Germain Pelet-Clozeau Papers')

    def test_MODS_record_contributor(self):
        self.assertEqual(self.record.contributor, [{'name': 'Winkler, '}])

    def test_MODS_record_creator(self):
        self.assertEqual(self.record.creator, [{'name': 'Mauldin, Bob'}])

    def test_MODS_record_date(self):
        self.assertEqual(self.record.date, {"begin": "1935", "end": "1969", "displayDate": "1935 - 1969"})

    def test_MODS_record_description(self):
        self.assertEqual(self.record.description, ["Test 00"])

    def test_MODS_record_extent(self):
        self.assertEqual(self.record.extent, ["8 x 10 in."])

    def test_MODS_record_format(self):
        self.assertEqual(self.record.format, [{"name": "Photographs"}])

    def test_MODS_record_identifier(self):
        self.assertEqual(self.record.identifier, "http://purl.flvc.org/fsu/fd/FSUspcn329b")

    def test_MODS_record_language(self):
        self.assertEqual(self.record.language, [{"name": "English", "iso_639_3": "eng"}])

    def test_MODS_record_place(self):
        self.assertEqual(self.record.place, {"name": "Narnia"})

    def test_MODS_record_publisher(self):
        self.assertEqual(self.record.publisher, ["Tay Tay Frankie"])

    def test_MODS_record_rights(self):
        self.assertEqual(self.record.rights, ['http://rightsstatements.org/vocab/NoC-US/1.0/', 'Rights 4A'])

    def test_MODS_record_subject(self):
        self.assertEqual(self.record.subject, [{'name': 'Students'}, {'name': 'Greek life'}, {'name': 'Fraternities and Sororities'}, {'name': 'Narnia'}])

    def test_MODS_record_title(self):
        self.assertEqual(self.record.title, 'Fraternity fundraiser for injured student')

    def test_MODS_record_type(self):
        self.assertEqual(self.record.type, "still image")


# def suite():
#     test_suite = unittest.TestSuite(tests=ScenariosTestCase)
#     test_suite.addTest(ScenariosTestCase)
#     test_suite.addTest(CitrusRecordTestCase)
#     test_suite.addTest(DC_RecordTestCase)
#     test_suite.addTest(QDC_RecordTestCase)
#     test_suite.addTest(MODS_RecordTestCase)
#     return test_suite


if __name__ == '__main__':
    unittest.main()
