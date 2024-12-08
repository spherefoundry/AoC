import unittest
from dataclasses import dataclass
from enum import StrEnum
from typing import Self, Tuple

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse


class Field(StrEnum):
    EMPTY = '.'
    CRATE = '#'
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


type Path = dict[Position, set[Field]]


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
        obstacles: set[Position] = set()
        path, is_loop = self.walk_internal(self.guard_position, self.guard_direction, None)
        if is_loop:
            return 0

        for position in path:
            for direction in path[position]:
                candidate_obstacle = position.move(direction)
                if not self.guard(candidate_obstacle):
                    continue
                new_path, is_loop = self.walk_internal(position, direction, candidate_obstacle)
                if is_loop:
                    obstacles.add(position.move(direction))

        return len(obstacles)

    def walk_internal(self, position: Position, direction: Field, additional_obstacle: Position | None) -> Tuple[Path, bool]:
        path: Path = {}
        while True:
            next_position = position.move(direction)
            if not self.guard(next_position):
                break

            next_field = self.get(next_position)
            if next_field == Field.CRATE or next_position == additional_obstacle:
                direction = direction.turn_right()
            else:
                if position in path:
                    if direction in path[position]:
                        # loop
                        return path, True
                    else:
                        path[position].add(direction)
                else:
                    path[position] = {direction}

                position = next_position
        return path, False

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

    def print(self):
        for iy in range(self.dim_y):
            line = "".join([self.get(Position(ix, iy)) for ix in range(self.dim_x)])
            print(f"{line}")


type LineModel = str


def load_line(num: int, line: str) -> LineModel:
    return line.strip()


def task(filename: str) -> int:
    lines = parse(filename, load_line)
    map = Map(list(lines))
    return map.walk()


class TestCases(unittest.TestCase):
    def test_example(self):
        self.assertEqual(task(data_example_filename()), 6)

    def test_task(self):
        self.assertEqual(task(data_filename()), 2013)
