import unittest
from dataclasses import dataclass
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse


@dataclass
class Report:
    values: list[int]

    @classmethod
    def parse(cls, line: str) -> Self:
        return cls([int(v.strip()) for v in line.split(" ") if v != ''])

    @property
    def is_safe(self) -> bool:
        prev = None
        is_increasing = None
        for v in self.values:
            if prev is None:
                prev = v
                continue

            if v == prev:
                return False

            if abs(v - prev) > 3:
                return False

            if is_increasing is None:
                is_increasing = v > prev

            if is_increasing:
                if v < prev:
                    return False
            else:
                if v > prev:
                    return False
            prev = v
        return True


type LineModel = Report


def load_line(num: int, line: str) -> LineModel:
    return Report.parse(line)


def task(filename: str) -> int:
    ret = 0
    lines = parse(filename, load_line)
    for line in lines:
        if line.is_safe:
            ret += 1
    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "7 6 4 2 1"), Report([7, 6, 4, 2, 1]))

    def test_is_safe(self):
        self.assertTrue(Report([7, 6, 4, 2, 1]).is_safe)
        self.assertTrue(Report([1, 3, 6, 7, 9]).is_safe)
        self.assertFalse(Report([1, 2, 7, 8, 9]).is_safe)
        self.assertFalse(Report([9, 7, 6, 2, 1]).is_safe)
        self.assertFalse(Report([1, 3, 2, 4, 5]).is_safe)
        self.assertFalse(Report([8, 6, 4, 4, 1]).is_safe)

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 2)

    def test_task(self):
        self.assertEqual(task(data_filename()), 510)
