import json
import os
import unittest

test_dir_path = os.path.abspath(os.path.dirname(__file__))


# class SourceResourceTestCase(unittest.TestCase):
#
#     def test_something(self):
#         self.assertEqual(True, True)


class SourceResourceRecordTestCase(unittest.TestCase):

    def setUp(self):
        from citrus.source_resource import Record
        self.rec = Record()
        self.rec['spam'] = 'eggs'
        self.rec['pining'] = 'fjords'

    def test_record_contains_true(self):
        self.assertTrue('spam' in self.rec)

    def test_record_contains_false(self):
        self.assertFalse('ham' in self.rec)

    def test_record_iter(self):
        i = 0
        for _ in self.rec:
            i = i + 1
        self.assertEqual(i, 2)

    def test_record_delitem(self):
        del self.rec['spam']
        self.assertFalse('spam' in self.rec)

    def test_record_delitem_error(self):
        def raise_key_error():
            del self.rec['ham']

        self.assertRaises(KeyError, raise_key_error)

    def test_record_getitem(self):
        self.assertTrue(self.rec['spam'] == 'eggs')

    def test_record_getitem_error(self):
        def raise_key_error():
            self.rec['ham'] == 'eggs'

        self.assertRaises(KeyError, raise_key_error)

    def test_record_setattr(self):
        self.rec.beans = 'toast'
        self.assertTrue(self.rec.__dict__['beans'] == 'toast')

    def test_record_setitem(self):
        self.rec['parrot'] = 'sleeping'
        self.assertTrue(self.rec.__dict__['parrot'] == 'sleeping')

    def test_record_dumps(self):
        self.assertDictEqual({"spam": "eggs", "pining": "fjords"}, json.loads(self.rec.dumps()))

    def test_record_data(self):
        self.assertDictEqual({"spam": "eggs", "pining": "fjords"}, self.rec.data)

    def test_record_keys(self):
        k_list = [k for k in self.rec.keys()]
        self.assertListEqual(k_list, ['spam', 'pining'])


class SourceResourceSourceResourceTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import SourceResource
        self.sr = SourceResource()

    def test_source_resource_rights_error(self):
        from citrus import SourceResourceRequiredElementException

        def raise_error():
            self.sr.rights = None

        self.assertRaises(SourceResourceRequiredElementException, raise_error)

    def test_source_resource_title_error(self):
        from citrus import SourceResourceRequiredElementException

        def raise_error():
            self.sr.title = None

        self.assertRaises(SourceResourceRequiredElementException, raise_error)


class SourceResourceRecordGroupTestCase(unittest.TestCase):

    def setUp(self):
        from citrus import RecordGroup
        self.rg = RecordGroup()
        self.rg.load(os.path.join(test_dir_path, 'test_data/record_group_jsonl.jsonl'))

    def test_record_group_len(self):
        self.assertEqual(len(self.rg), 8)

    def test_record_group_iter(self):
        i = 0
        for _ in self.rg:
            i = i + 1
        self.assertEqual(i, 8)

    def test_record_group_append(self):
        self.rg.append('{record}')
        self.assertEqual(len(self.rg), 9)

    def test_record_group_write_json(self):
        from datetime import date
        self.rg.write_json(os.path.join(test_dir_path, 'mock_temp_dir'))
        self.assertTrue(os.path.exists(os.path.join(test_dir_path, f'mock_temp_dir/{date.today()}.json')))
        os.remove(os.path.join(test_dir_path, f'mock_temp_dir/{date.today()}.json'))
        os.removedirs(os.path.join(test_dir_path, f'mock_temp_dir'))

    def test_record_group_write_jsonl(self):
        from datetime import date
        self.rg.write_jsonl(os.path.join(test_dir_path, 'mock_temp_dir'))
        self.assertTrue(os.path.exists(os.path.join(test_dir_path, f'mock_temp_dir/{date.today()}.jsonl')))
        os.remove(os.path.join(test_dir_path, f'mock_temp_dir/{date.today()}.jsonl'))
        os.removedirs(os.path.join(test_dir_path, f'mock_temp_dir'))

    # def test_record_group_write_print(self):
    #     pass

    def test_record_group_load_json(self):
        from citrus import RecordGroup
        rg = RecordGroup()
        rg.load(os.path.join(test_dir_path, 'test_data/record_group_json.json'))
        self.assertEqual(len(rg), 8)

    def test_record_group_load_jsonl(self):
        from citrus import RecordGroup
        rg = RecordGroup()
        rg.load(os.path.join(test_dir_path, 'test_data/record_group_jsonl.jsonl'))
        self.assertEqual(len(rg), 8)


if __name__ == '__main__':
    unittest.main()
