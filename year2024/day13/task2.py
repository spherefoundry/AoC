import unittest
from dataclasses import dataclass
from typing import Self, Tuple

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines, LineStream, parse


@dataclass
class Challenge:
    button_a_x: int
    button_a_y: int
    button_b_x: int
    button_b_y: int
    prize_x: int
    prize_y: int

    @classmethod
    def parse(cls, stream: LineStream) -> Self:
        def parse_line(expected: str, separator: str, line: str) -> Tuple[int, int] | None:
            line = line.strip()
            if len(line) == 0:
                return None

            prefix, values = line.split(":", maxsplit=1)
            if prefix != expected:
                return None
            x_part, y_part = values.split(",", maxsplit=1)
            x_part_left, x_part_right = x_part.strip().split(separator, maxsplit=1)
            y_part_left, y_part_right = y_part.strip().split(separator, maxsplit=1)
            if x_part_left != 'X' or y_part_left != 'Y':
                return None
            return int(x_part_right), int(y_part_right)


        while True:
            if (button_a := parse_line("Button A", "+", next(stream))) is None:
                continue
            if (button_b := parse_line("Button B", "+", next(stream))) is None:
                continue
            if (prize := parse_line("Prize", "=", next(stream))) is None:
                continue
            return cls(
                button_a[0],
                button_a[1],
                button_b[0],
                button_b[1],
                prize[0] + 10000000000000,
                prize[1] + 10000000000000
            )

    def cost(self) -> int:
        a = (self.prize_y * self.button_b_x - self.prize_x * self.button_b_y) / (self.button_a_y * self.button_b_x - self.button_a_x * self.button_b_y)
        if not a.is_integer():
            return 0

        b = (self.prize_y * self.button_a_x - self.prize_x * self.button_a_y) / (
                    self.button_b_y * self.button_a_x - self.button_b_x * self.button_a_y)
        if not b.is_integer():
            return 0

        return int(a) * 3 + int(b)

        # p1 = (self.prize_y * self.button_a_x / self.button_a_y - self.prize_x)
        # p2 = (self.button_b_y * self.button_a_x / self.button_a_y - self.button_b_x)
        # if p2 == 0:
        #     return 0
        # b = p1 / p2
        # if not b.is_integer():
        #     return 0
        # b = int(b)
        #
        # p1 = self.prize_y - self.prize_x - b * (self.button_b_y - self.button_b_x)
        # p2 = self.button_a_y - self.button_a_x
        # if p2 == 0:
        #     return 0
        # a = p1 / p2
        # if not a.is_integer():
        #     return 0
        # a = int(a)
        # return a * 3 + b


type Model = Challenge


def task(filename: str) -> int:
    ret = 0
    items = parse(filename, Challenge.parse)
    for item in items:
        ret += item.cost()
    return ret


class TestCases(unittest.TestCase):
    def test_parse(self):
        stream = LineStream.from_string("""
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400
        """)
        self.assertEqual(Challenge.parse(stream), Challenge(94, 34, 22, 67, 8400 + 10000000000000, 5400 + 10000000000000))

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 875318608908)

    def test_task(self):
        self.assertEqual(task(data_filename()), 73458657399094)
