import unittest
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines


@dataclass(frozen=True)
class Operation:
    x: int
    y: int

    def value(self) -> int:
        return self.x * self.y


@dataclass(frozen=True)
class Row:
    operations: list[Operation]

    @classmethod
    def parse(cls, line: str) -> Self:
        i = 0
        operations = []

        while i < len(line):
            if (op := cls.parse_operation(line, i)) is not None:
                operations.append(op)
            i += 1

        return cls(operations)

    @classmethod
    def parse_operation(cls, line: str, start_index: int) -> Operation | None:
        i = start_index
        if line[i] != "m" or line[i + 1] != "u" or line[i + 2] != "l" or line[i + 3] != "(":
            return None
        i += 4
        x = 0
        ix = 0
        while ix <= 3:
            ch = line[i + ix]
            if ch == ',':
                break
            elif str.isdigit(ch):
                x = x * 10 + int(ch)
                ix += 1
            else:
                return None

        if ix > 3 or line[i+ix] != ',':
            return None

        i = i + ix + 1

        y = 0
        iy = 0
        while iy <= 3:
            ch = line[i + iy]
            if ch == ')':
                break
            elif str.isdigit(ch):
                y = y * 10 + int(ch)
                iy += 1
            else:
                return None

        if iy > 3 or line[i+iy] != ')':
            return None

        return Operation(x, y)

type LineModel = Row


def load_line(num: int, line: str) -> LineModel:
    return Row.parse(line)


def task(filename: str) -> int:
    ret = 0
    lines = parse_lines(filename, load_line)
    for line in lines:
        for op in line.operations:
            ret += op.value()
    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "mul(2567,5)"), Row([]))

        self.assertEqual(load_line(0, "xul(0, 0)"), Row([]))
        self.assertEqual(load_line(0, "mul(2, 5)"), Row([]))
        self.assertEqual(load_line(0, "mul( 2,5)"), Row([]))
        self.assertEqual(load_line(0, "mul(2,5 )"), Row([]))

        self.assertEqual(load_line(0, "mul(25,5123)"), Row([]))
        self.assertEqual(load_line(0, "mul(2,5)"), Row([Operation(2, 5)]))
        self.assertEqual(load_line(0, "mul(234,125)"), Row([Operation(234, 125)]))
        self.assertEqual(load_line(0, "abcmul(2,5)123"), Row([Operation(2, 5)]))
        self.assertEqual(load_line(0, "abcmul(2,5)123mul(34,21)"), Row([Operation(2, 5), Operation(34, 21)]))

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 161)

    def test_task(self):
        self.assertEqual(task(data_filename()), 173419328)
