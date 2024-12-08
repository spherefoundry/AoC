import unittest
from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse


class Field(StrEnum):
    EMPTY = '.'
    CRATE = '#'
    VISITED = "X"
    GUARD_UP = "^"
    GUARD_DOWN = "V"
    GUARD_LEFT = "<"
    GUARD_RIGHT = ">"

    @property
    def is_guard(self) -> bool:
        return self == Field.GUARD_UP or self == Field.GUARD_DOWN or self == Field.GUARD_LEFT or self == Field.GUARD_RIGHT

    def turn_right(self) -> Self:
        match self:
            case Field.GUARD_UP:
                return Field.GUARD_RIGHT
            case Field.GUARD_RIGHT:
                return Field.GUARD_DOWN
            case Field.GUARD_DOWN:
                return Field.GUARD_LEFT
            case Field.GUARD_LEFT:
                return Field.GUARD_UP
        exit(1)


type LineModel = str


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def move(self, field: Field) -> Self:
        match field:
            case Field.GUARD_UP:
                return Position(self.x, self.y - 1)
            case Field.GUARD_DOWN:
                return Position(self.x, self.y + 1)
            case Field.GUARD_LEFT:
                return Position(self.x - 1, self.y)
            case Field.GUARD_RIGHT:
                return Position(self.x + 1, self.y)


class Map:
    def __init__(self, input: list[str]):
        fields = []
        iy = 0
        for line in input:
            ix = 0
            for char in line:
                field = Field(char)
                if field.is_guard:
                    self.guard_position = Position(ix, iy)
                    self.guard_direction = field
                    fields.append(Field.EMPTY)
                else:
                    fields.append(field)
                ix += 1
            iy += 1
        self.fields = fields
        self.dim_x = len(input[0])
        self.dim_y = len(input)

    def walk(self) -> int:
        ret = 1
        visited: dict[Position, set[Field]] = {
        }
        while True:
            next_position = self.guard_position.move(self.guard_direction)
            if not self.guard(next_position):
                break

            next_field = self.get(next_position)
            if next_field == Field.CRATE:
                self.guard_direction = self.guard_direction.turn_right()
            else:
                if self.guard_position in visited:
                    if self.guard_direction in visited[self.guard_position]:
                        # loop
                        return ret
                    else:
                        visited[self.guard_position].add(self.guard_direction)
                else:
                    ret += 1
                    visited[self.guard_position] = {self.guard_direction}

                self.guard_position = next_position
        return ret

    def get(self, position: Position) -> Field | None:
        if not self.guard(position):
            return None
        return self.fields[position.y * self.dim_x + position.x]

    def set(self, position: Position, field: Field):
        if not self.guard(position):
            return None
        self.fields[position.y * self.dim_x + position.x] = field

    def guard(self, position: Position) -> bool:
        return 0 <= position.x < self.dim_x and 0 <= position.y < self.dim_y


def load_line(num: int, line: str) -> LineModel:
    return line.strip()


def task(filename: str) -> int:
    lines = parse(filename, load_line)
    map = Map(list(lines))
    return map.walk()


class TestCases(unittest.TestCase):
    def test_example(self):
        self.assertEqual(task(data_example_filename()), 41)

    def test_task(self):
        self.assertEqual(task(data_filename()), 5444)
