import unittest


class ScenariosTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import Scenario
        self.scenario = Scenario('citrus/tests/test_data/DCdebugSmall.xml')

    def test_deleted_records(self):
        self.assertEqual(len(self.scenario), 3)


# class SSDN_DCTestCase(ScenariosTestCase):
#     #from citrus import SSDN_DC
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# class SSDN_QDCTestCase(ScenariosTestCase):
#     #from citrus import SSDN_QDC
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# class SSDN_MODSTestCase(ScenariosTestCase):
#     #from citrus import SSDN_MODS
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# class CitrusRecordTestCase(unittest.TestCase):
#     #from citrus import CitrusRecord
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# class DC_RecordTestCase(CitrusRecordTestCase):
#     #from citrus import DC_Record
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# class QDC_RecordTestCase(CitrusRecordTestCase):
#     #from citrus import QDC_Record
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# class MODS_RecordTestCase(CitrusRecordTestCase):
#     #from citrus import MODS_Record
#
#     # def test_something(self):
#     #     self.assertEqual(True, False)
#
#
# # def suite():
# #     scenario_suite = unittest.TestSuite((ScenariosTestCase, ))
# #     test_suite = unittest.TestSuite((scenario_suite, ))
# #     return test_suite


if __name__ == '__main__':
    unittest.main()
