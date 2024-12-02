import os.path
import unittest
import inspect

def __caller_filename() -> str:
    # note: we assume the caller is two levels lower in the stack, with the called function and this helper on top
    _,filename,_,_,_,_ = inspect.stack()[2]
    return filename

def data_example_filename() -> str:
    root, ext = os.path.splitext(__caller_filename())
    _, tail = os.path.split(root)
    return tail + "_example.txt"

def data_filename() -> str:
    root, ext = os.path.splitext(__caller_filename())
    _, tail = os.path.split(root)
    return tail + ".txt"


class TestCases(unittest.TestCase):
    def test_data_example_filename(self):
        self.assertEqual("file_example.txt", data_example_filename())

    def test_data_filename(self):
        self.assertEqual("file.txt", data_filename())