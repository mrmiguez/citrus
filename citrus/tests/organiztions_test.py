import os
import unittest

test_dir_path = os.path.abspath(os.path.dirname(__file__))


class DataProviderTestCase(unittest.TestCase):

    def setUp(self):
        from citrus.organizations import DataProvider
        import configparser
        self.scenario_config = configparser.ConfigParser()
        self.scenario_config.read(os.path.join(test_dir_path, 'test_data/test_scenario_config.cfg'))
        self.data_provider = DataProvider()
        section = 'fsu'
        self.data_provider.key = section
        self.data_provider.scenario = self.scenario_config[section]['scenario']
        self.data_provider.map = self.scenario_config[section]['map']
        self.data_provider.data_provider = self.scenario_config[section]['dataprovider']
        self.data_provider.intermediate_provider = self.scenario_config[section].get('intermediateprovider')

    def test_data_provider_key(self):
        self.assertEqual(self.data_provider.key, 'fsu')

    def test_data_provider_scenario(self):
        self.assertEqual(self.data_provider.scenario, 'SSDNMODS')

    def test_data_provider_map(self):
        self.assertEqual(self.data_provider.map, 'fsu_mods_map')

    def test_data_provider_data_provider(self):
        self.assertEqual(self.data_provider.data_provider, 'FSU')

    def test_data_intermediate_provider(self):
        self.assertEqual(self.data_provider.intermediate_provider, 'None')


if __name__ == '__main__':
    unittest.main()
