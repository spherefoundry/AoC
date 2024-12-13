import unittest
from dataclasses import dataclass

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines


@dataclass
class Line:
    left: int
    right: int


type LineModel = Line


def load_line(num: int, line: str) -> LineModel:
    values = [v for v in line.split(" ") if v != '']
    return Line(int(values[0]), int(values[1]))


def task(filename: str) -> int:
    ret = 0
    lines = parse_lines(filename, load_line)
    left = []
    right = []
    for line in lines:
        left.append(line.left)
        right.append(line.right)
    left.sort()
    right.sort()

    for i in range(len(left)):
        ret += abs(left[i] - right[i])

    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "3   4"), Line(3, 4))

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 11)

    def test_task(self):
        self.assertEqual(task(data_filename()), 2086478)
