# tests/test_read_file.py
import unittest
from tools.read_file import read_file
import os

class TestReadFile(unittest.TestCase):
    def test_read_file_exists(self):
        # Create a test file
        with open('test_file.txt', 'w') as f:
            f.write('Hello, World!')
        
        # Test reading the file
        self.assertEqual(read_file('test_file.txt'), 'Hello, World!')
        
        # Remove the test file
        os.remove('test_file.txt')
    
    def test_read_file_does_not_exist(self):
        # Test reading a non-existent file
        with self.assertRaises(FileNotFoundError):
            read_file('non_existent_file.txt')
    
    def test_read_file_empty(self):
        # Create an empty test file
        open('empty_test_file.txt', 'w').close()
        
        # Test reading the empty file
        self.assertEqual(read_file('empty_test_file.txt'), '')
        
        # Remove the test file
        os.remove('empty_test_file.txt')
    
    def test_read_file_large(self):
        # Create a large test file
        with open('large_test_file.txt', 'w') as f:
            for _ in range(10000):
                f.write('Hello, World!\n')
        
        # Test reading the large file
        with open('large_test_file.txt', 'r') as f:
            expected_contents = f.read()
        self.assertEqual(read_file('large_test_file.txt'), expected_contents)
        
        # Remove the test file
        os.remove('large_test_file.txt')

if __name__ == '__main__':
    unittest.main()