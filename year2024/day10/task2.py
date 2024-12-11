import unittest
from dataclasses import dataclass, field
from email.policy import default
from typing import Self, Sequence

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse

type LineModel = list[int]


def load_line(num: int, line: str) -> LineModel:
    return [int(ch) for ch in line.strip()]


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def neighbors(self) -> Sequence[Self]:
        yield Position(self.x + 1, self.y)
        yield Position(self.x, self.y + 1)
        yield Position(self.x - 1, self.y)
        yield Position(self.x, self.y - 1)


@dataclass
class Node:
    value: int
    position: Position
    next: list[Self] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"(Node({self.position.x, self.position.y} -> {self.value})"


class Map:
    def __init__(self, input: list[list[int]]):
        self.dim_x = len(input[0])
        self.dim_y = len(input)

        nodes = []
        for iy, line in enumerate(input):
            for ix, value in enumerate(line):
                nodes.append(Node(value, Position(ix, iy)))

        self.nodes = nodes
        for node in self.nodes:
            for np in node.position.neighbors():
                if not self.guard(np):
                    continue
                neighbor = self.get(np)
                if neighbor.value == node.value + 1:
                    node.next.append(neighbor)

    def walk_all(self) -> int:
        ret = 0
        for node in self.nodes:
            if node.value != 0:
                continue
            ret += self.walk_starting(node.position)
        return ret

    def walk_starting(self, position: Position) -> int:
        waiting = [self.get(position)]
        visited: dict[Position, int] = {position: 1}
        end_positions = set()
        while waiting:
            node = waiting.pop(0)
            rating = visited[node.position]
            for nn in node.next:
                if nn.value == 9:
                    end_positions.add(nn.position)
                if nn.position not in visited:
                    waiting.append(nn)
                visited[nn.position] = visited.get(nn.position, 0) + rating
        return sum([visited[p] for p in end_positions])

    def get(self, position: Position) -> Node:
        assert self.guard(position)
        return self.nodes[position.y * self.dim_x + position.x]

    def set(self, position: Position, field: Node):
        if not self.guard(position):
            return None
        self.nodes[position.y * self.dim_x + position.x] = field

    def guard(self, position: Position) -> bool:
        return 0 <= position.x < self.dim_x and 0 <= position.y < self.dim_y


def task(filename: str) -> int:
    lines = list(parse(filename, load_line))
    map = Map(lines)
    return map.walk_all()


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "123"), [1, 2, 3])

    def test_map_construction(self):
        map = Map([[1, 2, 3], [3, 3, 5]])
        self.assertEqual(map.dim_x, 3)
        self.assertEqual(map.dim_y, 2)

        node0 = map.get(Position(0, 0))
        self.assertEqual(node0.value, 1)
        self.assertEqual(node0.position, Position(0, 0))
        node1 = map.get(Position(2, 1))
        self.assertEqual(node1.value, 5)
        self.assertEqual(node1.position, Position(2, 1))

        self.assertTrue(map.get(Position(1, 0)) in map.get(Position(0, 0)).next)
        self.assertFalse(map.get(Position(0, 1)) in map.get(Position(0, 0)).next)
        self.assertTrue(map.get(Position(2, 0)) in map.get(Position(1, 0)).next)
        self.assertTrue(map.get(Position(1, 1)) in map.get(Position(1, 0)).next)

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 81)

    def test_task(self):
        self.assertEqual(task(data_filename()), 1324)
