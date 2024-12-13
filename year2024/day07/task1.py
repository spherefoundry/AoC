import unittest
from dataclasses import dataclass
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines


@dataclass
class Row:
    value: int
    parts: list[int]

    @classmethod
    def parse(cls, line: str) -> Self:
        value_segment, rest = line.strip().split(":", 1)
        separated = [int(v.strip()) for v in rest.split(" ") if v != '']
        return cls(int(value_segment.strip()), separated)

    def calibrate(self) -> int:
        if len(self.parts) == 0:
            return 0
        if len(self.parts) == 1:
            return 1 if self.parts[0] == self.value else 0

        ret = 0
        last_part = self.parts[-1]
        new_parts = self.parts[:-1]
        if self.value % last_part == 0:
            ret += Row(self.value // last_part, new_parts).calibrate()

        ret += Row(self.value - last_part, new_parts).calibrate()

        return ret

type LineModel = Row


def load_line(num: int, line: str) -> LineModel:
    return Row.parse(line)


def task(filename: str) -> int:
    ret = 0
    rows = parse_lines(filename, load_line)
    for row in rows:
        if row.calibrate() > 0:
            ret += row.value
    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "64288413730: 91 79 4 9 7 8 91 7 30"), Row(64288413730, [91, 79, 4, 9, 7, 8, 91, 7, 30]))

    def test_calibrate(self):
        self.assertEqual(Row.parse("190: 10 19").calibrate(), 1)
        self.assertEqual(Row.parse("3267: 81 40 27").calibrate(), 2)
        self.assertEqual(Row.parse("292: 11 6 16 20").calibrate(), 1)
        self.assertEqual(Row.parse("83: 17 5").calibrate(), 0)
        self.assertEqual(Row.parse("7290: 6 8 6 15").calibrate(), 0)

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 3749)

    def test_task(self):
        self.assertEqual(task(data_filename()), 4122618559853)
