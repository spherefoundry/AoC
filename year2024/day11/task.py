import unittest
from dataclasses import dataclass, field
from typing import Self, Sequence, Tuple

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse

def separate_digits(v: int) -> list[int]:
    ret = []
    while v > 0:
        ret.append(v % 10)
        v //= 10
    ret.reverse()
    return ret

def merge_digits(digits: list[int], start: int, len: int) -> int:
    ret = 0
    for i in range(start, start + len):
        ret = ret * 10 + digits[i]
    return ret

@dataclass
class Node:
    value: int
    end_of_stone: bool = False
    next: Self = None
    prev: Self = field(default=None, init=False, compare=False)

    @classmethod
    def parse(cls, line: str) -> Self:
        values = [int(v) for v in line.strip().split()]
        first_node = None
        it = None
        for v in values:
            for digit in separate_digits(v):
                if first_node is None:
                    first_node = Node(digit)
                    it = first_node
                else:
                    it.next = Node(digit)
                    it.next.prev = it
                    it = it.next
            it.end_of_stone = True

        return first_node

    def blink_all(self):
        it = self
        while it is not None:
            stone_head = it
            stone_tail, stone_len = it.find_tail_of_stone()

            if stone_len == 1 and stone_head.value == 0:
                stone_head.value = 1
            elif stone_len % 2 == 0:
                stone_middle = stone_head.walk(stone_len // 2 - 1)
                stone_middle.end_of_stone = True
                stone_middle.next = stone_middle.next.prune_zeros()
                stone_middle.next.prev = stone_middle
            else:
                stone_tail = stone_head.multiply(2024)

            it = stone_tail.next

    def find_tail_of_stone(self) -> Tuple[Self, int]:
        it = self
        num = 0
        while it is not None:
            num += 1
            if it.end_of_stone:
                return it, num
            it = it.next

    def count_stones(self) -> int:
        ret = 0
        it = self
        while it is not None:
            if it.end_of_stone:
                ret += 1
            it = it.next
        return ret

    def walk(self, distance: int) -> Self | None:
        it = self
        while it is not None and distance > 0:
            it = it.next
            distance -= 1
        return it

    def prune_zeros(self) -> Self:
        it = self
        while it is not None and it.value == 0 and not it.end_of_stone:
            it = it.next
        return it


    def multiply(self, multiplier: int) -> Self:
        rest = 0
        head = self
        tail, len = self.find_tail_of_stone()
        it = tail
        while True:
            v = it.value * multiplier + rest
            if it != head:
                it.value = v % 10
                rest = v // 10
                it = it.prev
            else:
                while v >= 10:
                    node = Node(v % 10)
                    node.next = it.next
                    node.prev = it
                    if it.next is not None:
                        it.next.prev = node
                    it.next = node
                    if it.end_of_stone:
                        node.end_of_stone = True
                        it.end_of_stone = False
                        tail = node
                    v //= 10
                it.value = v
                return tail

    def __repr__(self):
        return f"{self.value} {"|| " if self.end_of_stone else ""}- {self.next.__repr__() if self.next is not None else "None"}"



# @dataclass
# class Stone:
#     value: int
#     next: Self = None
#
#     def blink(self) -> Self:
#         if self.value == 0:
#             self.value = 1
#             return self
#
#         digits = separate_digits(self.value)
#         if len(digits) % 2 == 0:
#             half= len(digits) // 2
#             self.add_after(merge_digits(digits, half, half))
#             self.value = merge_digits(digits, 0, half)
#             return self
#
#         self.value = self.value * 2024
#         return self
#
#
#     def add_after(self, value: int):
#         new_stone = Stone(value, self.next)
#         self.next = new_stone
#
#     def as_list(self) -> Sequence[int]:
#         it = self
#         while it is not None:
#             yield it.value
#             it = it.next
#
#     def count(self) -> int:
#         ret = 0
#         it = self
#         while it is not None:
#             ret += 1
#             it = it.next
#         return ret


type LineModel = Node

def load_line(num: int, line: str) -> LineModel:
    return Node.parse(line)


def task(filename: str, num_blinks: int) -> int:
    first_node = next(parse(filename, load_line))
    for i in range(num_blinks):
        print(f"blink: {i}")
        first_node.blink_all()
    return first_node.count_stones()


class TestCases(unittest.TestCase):
    def test_load_line(self):
        subject = load_line(0, "125 17")
        self.assertEqual(subject.value, 1)
        self.assertFalse(subject.end_of_stone)
        subject = subject.next
        self.assertEqual(subject.value, 2)
        self.assertFalse(subject.end_of_stone)
        subject = subject.next
        self.assertEqual(subject.value, 5)
        self.assertTrue(subject.end_of_stone)
        subject = subject.next
        self.assertEqual(subject.value, 1)
        self.assertFalse(subject.end_of_stone)

    def test_find_end_of_stone(self):
        subject = Node.parse("125 17")
        end, num = subject.find_tail_of_stone()
        self.assertEqual(end.value, 5)
        self.assertEqual(num, 3)

    def test_separate_digits(self):
        self.assertEqual(separate_digits(123), [1, 2, 3])

    def test_merge_digits(self):
        self.assertEqual(merge_digits([4, 5, 2], 0, 3), 452)
        self.assertEqual(merge_digits([4, 5, 2], 0, 2), 45)
        self.assertEqual(merge_digits([4, 5, 2], 2, 1), 2)

    def test_prune_zeros(self):
        self.assertEqual(Node.parse("1000").prune_zeros(), Node.parse("1000"))
        self.assertEqual(Node.parse("0100").prune_zeros(), Node.parse("100"))

    def test_multiply(self):
        head = Node.parse("234")
        head.multiply(2024)
        self.assertEqual(head, Node.parse("473616"))

        head = Node.parse("234 17")
        head.multiply(2024)
        self.assertEqual(head, Node.parse("473616 17"))

        head = Node.parse("1 17")
        head.multiply(2024)
        self.assertEqual(head, Node.parse("2024 17"))

    # def test_blink(self):
    #     self.assertEqual(Stone(0).blink(), Stone(1))
    #     self.assertEqual(Stone(10).blink(), Stone(1, Stone(0)))
    #     self.assertEqual(Stone(11).blink(), Stone(1, Stone(1)))
    #     self.assertEqual(Stone(1221).blink(), Stone(12, Stone(21)))
    #     self.assertEqual(Stone(2).blink(), Stone(4048))

    def test_example(self):
        self.assertEqual(task(data_example_filename(), 25), 55312)

    def test_task1(self):
        self.assertEqual(task(data_filename(), 25), 218956)

    def test_task2(self):
        self.assertEqual(task(data_filename(), 75), 0)