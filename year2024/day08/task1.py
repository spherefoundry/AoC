import unittest
from dataclasses import dataclass
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines


@dataclass(frozen=True)
class Vector:
    x: int
    y: int

    def add(self, other: Self) -> Self:
        return Vector(self.x + other.x, self.y + other.y)

    def sub(self, other: Self) -> Self:
        return Vector(self.x - other.x, self.y - other.y)

    def negate(self) -> Self:
        return Vector(-self.x, -self.y)

@dataclass(frozen=True)
class Node:
    position: Vector
    value: str


@dataclass
class Row:
    nodes: list[Node]
    dim: int
    
    @classmethod
    def parse(cls, num: int, line: str) -> Self:
        ret = []
        line = line.strip()
        for ix in range(len(line)):
            if line[ix] == '.':
                continue
            ret.append(Node(Vector(ix, num), line[ix]))

        return cls(ret, len(line))


type LineModel = Row


def load_line(num: int, line: str) -> LineModel:
    return Row.parse(num, line)


def task(filename: str) -> int:
    nodes = {}
    antinodes = set()
    lines = list(parse_lines(filename, load_line))
    for line in lines:
        for n in line.nodes:
            nl = nodes.get(n.value, [])
            nl.append(n)
            nodes[n.value] = nl

    size = Vector(lines[0].dim, len(lines))

    def guard(v : Vector) -> bool:
        return 0 <= v.x < size.x and 0 <= v.y < size.y

    for key in nodes.keys():
        nodes_of_key = nodes[key]
        for i in range(len(nodes_of_key) - 1):
            for j in range(i + 1, len(nodes_of_key)):
                pos_i = nodes_of_key[i].position
                pos_j = nodes_of_key[j].position

                diff = pos_i.sub(pos_j)

                candidate_a = pos_i.add(diff)
                if guard(candidate_a):
                    antinodes.add(candidate_a)

                candidate_b = pos_j.sub(diff)
                if guard(candidate_b):
                    antinodes.add(candidate_b)

    return len(antinodes)


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(3, "....a....."), Row([Node(Vector(4, 3), "a")], 10))
        self.assertEqual(load_line(3, "......"), Row([], 6))

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 14)

    def test_task(self):
        self.assertEqual(task(data_filename()), 426)
