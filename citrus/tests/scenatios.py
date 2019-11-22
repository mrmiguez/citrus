import unittest


class ScenariosTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


class SSDN_DCTestCase(ScenariosTestCase):
    def test_something(self):
        self.assertEqual(True, False)


class SSDN_QDCTestCase(ScenariosTestCase):
    def test_something(self):
        self.assertEqual(True, False)


class SSDN_MODSTestCase(ScenariosTestCase):
    def test_something(self):
        self.assertEqual(True, False)


class CitrusRecordTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


class DC_RecordTestCase(CitrusRecordTestCase):
    def test_something(self):
        self.assertEqual(True, False)


class QDC_RecordTestCase(CitrusRecordTestCase):
    def test_something(self):
        self.assertEqual(True, False)


class MODS_RecordTestCase(CitrusRecordTestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
