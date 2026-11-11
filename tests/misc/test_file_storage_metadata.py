import unittest
from app.models.file_storage_metadata import File_storage_metadata
import datetime


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.test_metadata = File_storage_metadata(1001, "document", "doc", 1024, datetime.datetime(2026, 11, 11, 11,11),"string")
        self.test_string_class_creation = "1001, document, doc, 1024, 11:11 11/11/2026 ,string"
        self.test_string_metadata_retrieval = "1001, document, doc, 1024, 2026-11-11 11:11:00, string"

    def test_repr(self):

        self.assertEqual(self.test_metadata.__repr__(), self.test_string_metadata_retrieval)

    def test_from_string(self):
        self.assertEqual(self.test_metadata.from_string(self.test_string_class_creation), self.test_metadata)

if __name__ == '__main__':
    unittest.main()
