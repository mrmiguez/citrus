import os
import unittest
from unittest.mock import Mock

from lxml import etree
from sickle.models import Record

import citrus

test_dir_path = os.path.abspath(os.path.dirname(__file__))


class MockSickle(unittest.mock.MagicMock):

    def __init__(self, *args, **kwargs):
        unittest.mock.MagicMock.__init__(self)

    def ListRecords(self, *args, **kwargs):
        set_spec = kwargs.get('set')
        with open(os.path.join(test_dir_path, f'test_data/{set_spec}.xml'), 'r') as fp:
            data = etree.parse(fp).getroot()
            return [Record(data)]


class MainHarvestTestCase(unittest.TestCase):

    def setUp(self):
        self.harvest_parser = {
            'fsu': {'OAIEndpoint': '', 'MetadataPrefix': 'mods', 'SetList': 'fsu_susanbradfordeppespapers'},
            'usf': {'OAIEndpoint': '', 'MetadataPrefix': 'oai_dc', 'SetList': 'usf_boucicault'},
            'um': {'OAIEndpoint': '', 'MetadataPrefix': 'oai_qdc', 'SetList': 'um_chc0336'}}
        with unittest.mock.patch('sickle.Sickle', new=MockSickle, spec=True):
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
