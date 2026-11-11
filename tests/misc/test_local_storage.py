import unittest
import app.services.local_storage as local_storage

class TestLocalStorage(unittest.TestCase):

    def setUp(self):
        self.storage = local_storage.LocalStorage()

    def test_write_metadata(self):
        pass

    def test_delete_metadata(self):
        pass

    def test_find_file_metadata_from_id(self):
        pass

    def test_create_metadata(self):
        pass

    def test_save_file(self):
        pass

    def test_delete_file(self):
        pass

    def tearDown(self) -> None:
        """filepath= Path(f"... /testing.txt)"""
        """filepath.unlink()"""
        pass

if __name__ == '__main__':
    unittest.main()
