import os
import unittest
from unittest.mock import Mock

import citrus

test_dir_path = os.path.abspath(os.path.dirname(__file__))


class MODSHarvestTestCase(unittest.TestCase):

    def setUp(self):
        self.harvest_parser = {'fsu': {'OAIEndpoint': '', 'MetadataPrefix': 'mods', 'SetList': 'fsu'},
                               'usf': {'OAIEndpoint': '', 'MetadataPrefix': 'oai_dc', 'SetList': 'usf'},
                               'um': {'OAIEndpoint': '', 'MetadataPrefix': 'oai_qdc', 'SetList': 'um'}}
        with unittest.mock.patch('sickle.Sickle'):
            for section in self.harvest_parser:
                self.records = citrus.cli.harvest(self.harvest_parser[section], section,
                                                  os.path.join(test_dir_path, 'mock_temp_dir'), 1)

    def tearDown(self):
        for section in self.harvest_parser:
            for f in os.listdir(os.path.join(test_dir_path, 'mock_temp_dir', section)):
                os.remove(os.path.join(test_dir_path, 'mock_temp_dir', section, f))
            os.removedirs(os.path.join(test_dir_path, 'mock_temp_dir', section))

    def test_data_write(self):
        for section in self.harvest_parser:
            self.assertEqual(os.path.exists(os.path.join(test_dir_path, 'mock_temp_dir', section)), True)


if __name__ == '__main__':
    unittest.main()
