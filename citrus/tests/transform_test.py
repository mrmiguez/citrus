import json
import os
import unittest
from datetime import date

# from citrus.maps import mods_standard_map
from citrus.cli import transform

test_dir_path = os.path.abspath(os.path.dirname(__file__))


class MainDCTransformTestCase(unittest.TestCase):

    def setUp(self):
        self.config = {'ssdn': {'InFilePath': os.path.join(test_dir_path, 'test_data'),
                                'OutFilePath': os.path.join(test_dir_path, 'test_data'),
                                'Provider': 'Sunshine State Digital Network',
                                'CustomMapPath': test_dir_path}}
        self.data = json.loads(
            '{"@context": "http://api.dp.la/items/context", "aggregatedCHO": "#sourceResource", "dataProvider": \
            "University of South Florida Libraries", "provider": {"@id": "UNDETERMINED", "name": \
            "Sunshine State Digital Network"}, "isShownAt": "oai:USFLDC:SFS0049735_00001", "sourceResource": \
            {"creator": [{"name": "Boucicault, Dion, 1820-1890 ( author )"}], "description": \
            ["Promptbook includes typed pages with extensive notes from the stenographer and minor notes from the author.", \
            "Includes cast list of performers."], "format": ["82 numbered leaves : plans", "24 cm"], "identifier": \
            "oai:USFLDC:SFS0049735_00001", "language": ["English"], "rights": [\
            "The University of South Florida Libraries believes that the Item is in the Public Domain under the laws of the United States, but a determination was not made as to its copyright status under the copyright laws of other countries. The Item may not be in the Public Domain under the laws of other countries."], \
            "subject": [{"name": "Promptbooks -- Manuscripts -- 19th century"}], "title": ["Marriage"], \
            "type": ["text"]}}')

    def tearDown(self):
        os.remove(os.path.join(test_dir_path, 'test_data', f'SSDN_TMP-{date.today()}.jsonl'))

    def test_main_dc_transform(self):
        transformation_info = {'Map': 'dc_standard_map',
                               'DataProvider': 'University of South Florida Libraries',
                               'IntermediateProvider': None,
                               'Scenario': 'SSDNDC'}
        transform(self.config, transformation_info, 'dc', 'ssdn', verbosity=1)
        with open(os.path.join(test_dir_path, 'test_data', f'SSDN_TMP-{date.today()}.jsonl')) as fp:
            test_data = json.load(fp)
        self.assertEqual(test_data, self.data)


class MainQDCTransformTestCase(unittest.TestCase):

            def setUp(self):
                self.config = {'ssdn': {'InFilePath': os.path.join(test_dir_path, 'test_data'),
                                        'OutFilePath': os.path.join(test_dir_path, 'test_data'),
                                        'Provider': 'Sunshine State Digital Network',
                                        'CustomMapPath': test_dir_path}}
                self.data = json.loads(
                    '{"@context": "http://api.dp.la/items/context", "aggregatedCHO": "#sourceResource", \
                    "dataProvider": "University of Miami Libraries", "provider": {"@id": "UNDETERMINED", "name": \
                    "Sunshine State Digital Network"}, "isShownAt": "oai:merrick.library.miami.edu:chc0336/421", \
                    "sourceResource": {"creator": [{"name": "Consuegra, Jes\u00fas"}], "date": ["1937-11-24"], \
                    "description": ["Sent from Havana to New York"], "format": ["Correspondence", "image/tiff"], \
                    "identifier": "oai:merrick.library.miami.edu:chc0336/421", "rights": \
                    ["The copyright and related rights status of this material is unknown. For additional information, please visit: http://merrick.library.miami.edu/digitalprojects/copyright.html", \
                    "http://rightsstatements.org/vocab/UND/1.0/"], "title": \
                    ["Jes\u00fas Consuegra letter to Gerardo Machado, November 24, 1937"], "type": ["Text"], \
                    "collection": ["University of Miami. Library. Cuban Heritage Collection", \
                    "Gerardo Machado y Morales Papers", "CHC0336"], "extent": ["1 item (1 p.)"]}}')

            def tearDown(self):
                os.remove(os.path.join(test_dir_path, 'test_data', f'SSDN_TMP-{date.today()}.jsonl'))

            def test_main_qdc_transform(self):
                transformation_info = {'Map': 'qdc_standard_map',
                                       'DataProvider': 'University of Miami Libraries',
                                       'IntermediateProvider': None,
                                       'Scenario': 'SSDNQDC'}
                transform(self.config, transformation_info, 'qdc', 'ssdn', verbosity=1)
                with open(os.path.join(test_dir_path, 'test_data', f'SSDN_TMP-{date.today()}.jsonl')) as fp:
                    test_data = json.load(fp)
                self.assertEqual(test_data, self.data)


class MainMODSTransformTestCase(unittest.TestCase):

    def setUp(self):
        self.config = {'ssdn': {'InFilePath': os.path.join(test_dir_path, 'test_data'),
                                'OutFilePath': os.path.join(test_dir_path, 'test_data'),
                                'Provider': 'Sunshine State Digital Network',
                                'CustomMapPath': test_dir_path}}
        self.data = json.loads(
            '{"@context": "http://api.dp.la/items/context", "aggregatedCHO": "#sourceResource", "dataProvider": \
            "Florida State University Libraries", "provider": {"@id": "UNDETERMINED", "name": \
            "Sunshine State Digital Network"}, "isShownAt": "oai:fsu.digital.flvc.org:fsu_370933", "sourceResource": \
            {"contributor": [{"name": "Levy Bros."}], "creator": [{"name": "Eppes, N.W."}], "date": {"displayDate": \
            "1894-01-01", "begin": "1894-01-01", "end": "1894-01-01"}, "extent": ["2 pages", "7 x 16 cm"], "format": \
            [{"name": "Money", "@id": "http://id.loc.gov/vocabulary/graphicMaterials/tgm006725"}], "identifier": \
            "oai:fsu.digital.flvc.org:fsu_370933", "language": [{"name": "English", "iso_639_3": "eng"}], "spatial": \
            {"name": "Checks--United States"}, "rights": "http://rightsstatements.org/vocab/InC/1.0/", "subject": \
            [{"@id": "http://id.loc.gov/vocabulary/graphicMaterials/tgm006725", "name": "Money"}, {"@id": \
            "http://id.loc.gov/vocabulary/graphicMaterials/tgm001917", "name": "Checks"}, {"@id": \
            "http://id.loc.gov/vocabulary/graphicMaterials/tgm001479", "name": "Business & finance"}, {"@id": \
            "http://id.loc.gov/authorities/subjects/sh85022834", "name": "Checks"}, {"@id": \
            "http://id.loc.gov/authorities/subjects/sh2008100311", "name": "Checks--United States"}, \
            {"@id": "http://id.loc.gov/authorities/subjects/sh85086790", "name": "Money"}], "title": \
            "Capital City Bank Check for $1.00 to Levy Bros, signed by N. W. Eppes", "type": "text"}}')

    def tearDown(self):
        os.remove(os.path.join(test_dir_path, 'test_data', f'SSDN_TMP-{date.today()}.jsonl'))

    def test_main_mods_transform(self):
        transformation_info = {'Map': 'mods_standard_map',
                               'DataProvider': 'Florida State University Libraries',
                               'IntermediateProvider': None,
                               'Scenario': 'SSDNMODS'}
        transform(self.config, transformation_info, 'mods', 'ssdn', verbosity=1)
        with open(os.path.join(test_dir_path, 'test_data', f'SSDN_TMP-{date.today()}.jsonl')) as fp:
            test_data = json.load(fp)
        self.assertEqual(test_data, self.data)


if __name__ == '__main__':
    unittest.main()
