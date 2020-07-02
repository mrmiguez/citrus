import os
import unittest

test_dir_path = os.path.abspath(os.path.dirname(__file__))


class DCStandardMapTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SSDNDC, dc_standard_map
        self.scenario = SSDNDC(os.path.join(test_dir_path, 'test_data/DCdebugSmall.xml'))
        for sr, _ in dc_standard_map(self.scenario[0]):
            self.sr = sr

    def test_dc_standard_map(self):
        self.assertEqual(self.sr.data, {'contributor': [{'name': 'Buckethead'}],
                                        'creator': [{'name': 'Lewis Carroll'}],
                                        'date': ['1974'],
                                        'description': ['1 postcard, postally unused',
                                                        'caption: "Alligator Joe watching the Young Alligators '
                                                        'Hatch."'],
                                        'format': ['Embroidery'],
                                        'identifier': 'oai:lib.fsu.edu.fiu:oai:uofm.library.fiu:oai:dpsobek:FI07050832_00001',
                                        'language': ['English'],
                                        'spatial': [{'name': 'Moon'}],
                                        'publisher': ['Miami, Florida: J.N. Chamberlain',
                                                      'Miami, Florida: J.N. Chamberlain'],
                                        'rights': ['Rights 4A'],
                                        'subject': [{'name': 'Alligators--Florida--Everglades.'}],
                                        'title': ['Alligator Joe watching the young alligators hatch'],
                                        'type': ['Text']})


class QDCStandardMapTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SSDNQDC, qdc_standard_map
        self.scenario = SSDNQDC(os.path.join(test_dir_path, 'test_data/QDCdebugSmall.xml'))
        for sr, _ in qdc_standard_map(self.scenario[0]):
            self.sr = sr

    def test_qdc_standard_map(self):
        self.assertEqual(self.sr.data, {'abstract': ['Test 000'],
                                        'alternative': ['covfefe'],
                                        'collection': ['University of Miami. Library. Special Collections',
                                                       'Alan Crockwell Collection',
                                                       'ASM0447'],
                                        'contributor': [{'name': 'Thee Oh Sees'}],
                                        'creator': [{'name': 'Gilpin, Vincent'}],
                                        'date': ['1933-09-03'],
                                        'description': ['Test 001'],
                                        'extent': ['1 letter'],
                                        'format': ['image/tiff'],
                                        'identifier': 'oai:lib.fsu.edu.umiami:oai:uofm.library.umiami:oai:merrick.library.miami.edu:asm0447/31',
                                        'language': ['eng'],
                                        'spatial': [{'name': 'Excelsior (Minn.)'}],
                                        'publisher': ['Arista Records'],
                                        'rights': ['Rights 4A',
                                                   'Copyright Undetermined http://rightsstatements.org/page/UND/1.0/'],
                                        'subject': [{'name': 'Gilpin, Vincent'},
                                                    {'name': 'Munroe, Patty'},
                                                    {'name': 'Munroe, Ralph, 1851-1933'},
                                                    {'name': 'Letters'}],
                                        'title': ['Vincent Gilpin letter to Patty Munroe, September 3, 1933'],
                                        'type': ['Tax return from a VIP']})


class MODSStandardMapTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SSDNMODS, mods_standard_map
        self.scenario = SSDNMODS(os.path.join(test_dir_path, 'test_data/MODSdebugSmall.xml'))
        for sr, _ in mods_standard_map(self.scenario[0]):
            self.sr = sr

    def test_mods_standard_map(self):
        self.assertEqual(self.sr.data, {'alternative': ['ALT: Fraternity fundraiser for injured student'],
                                        'collection': 'General Jean-Jacques-Germain Pelet-Clozeau Papers',
                                        'contributor': [{'name': 'Winkler, '}],
                                        'creator': [{'name': 'Mauldin, Bob'}],
                                        'date': {'begin': '1935', 'displayDate': '1935 - 1969', 'end': '1969'},
                                        'description': ['Test 00'],
                                        'extent': ['8 x 10 in.'],
                                        'format': [{'name': 'Photographs'}],
                                        'identifier': 'oai:lib.fsu.edu.fsu_digital_library:oai:fsu.digital.flvc.org:fsu_24694',
                                        'language': [{'iso_639_3': 'eng', 'name': 'English'}],
                                        'spatial': {'name': 'Narnia'},
                                        'publisher': ['Tay Tay Frankie'],
                                        'rights': 'http://rightsstatements.org/vocab/NoC-US/1.0/',
                                        'subject': [{'name': 'Students'},
                                                    {'name': 'Greek life'},
                                                    {'name': 'Fraternities and Sororities'},
                                                    {'name': 'Narnia'}],
                                        'title': 'Fraternity fundraiser for injured student',
                                        'type': 'still image'})


if __name__ == '__main__':
    unittest.main()
