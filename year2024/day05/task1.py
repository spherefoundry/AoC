import unittest
from dataclasses import dataclass, field
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse


@dataclass
class Rule:
    left: int
    right: int

    @classmethod
    def parse(cls, line: str) -> Self | None:
        separated = [v.strip() for v in line.strip().split("|")]
        if len(separated) != 2:
            return None
        return cls(int(separated[0]), int(separated[1]))


@dataclass
class Update:
    pages: list[int]

    @classmethod
    def parse(cls, line: str) -> Self | None:
        separated = [v.strip() for v in line.strip().split(",") if v != '']
        if len(separated) == 0:
            return None
        separated = [int(v) for v in separated]
        return cls(separated)

    @property
    def middle_value(self) -> int:
        return self.pages[len(self.pages) // 2]

    def verify_against_rules(self, rules: list[Rule]) -> bool:
        page_set = set(self.pages)
        valid_rules = [r for r in rules if r.left in page_set and r.right in page_set]
        for subject in range(len(self.pages) - 1):
            for candidate in range(subject + 1, len(self.pages)):
                for rule in valid_rules:
                    if rule.left == self.pages[candidate] and rule.right == self.pages[subject]:
                        return False

        return True


# class Node:
#     values: set[int] = field(default_factory=set)
#     left: Self | None = None
#     right: Self | None = None
#
#     def merge_rule(self, rule: Rule):
#
#
#     def verify_update(self, update: Update) -> bool:
#         return False
#
#     def check_in_left(self, value: int) -> bool:
#         return self.check_in_node(self.left, value)
#
#     def check_in_right(self, value: int) -> bool:
#         return self.check_in_node(self.right, value)
#
#     def check_in_node(self, node: Self | None, value: int) -> bool:
#         if node is None:
#             return False
#         return value in node.values


type LineModel = Rule | Update | None


def load_line(num: int, line: str) -> LineModel:
    if (rule := Rule.parse(line)) is not None:
        return rule
    if (update := Update.parse(line)) is not None:
        return update
    return None


def task(filename: str) -> int:
    ret = 0
    lines = parse(filename, load_line)
    # root_node = Node()
    # for line in lines:
    #     if type(line) is Rule:
    #         root_node.merge_rule(line)
    #     if type(line) is Update:
    #         if root_node.verify_update(line):
    #             ret += line.middle_value

    rules : list[Rule] = []
    updates : list[Update] = []
    for line in lines:
        if type(line) is Rule:
            rules.append(line)
        if type(line) is Update:
            updates.append(line)

    for update in updates:
        if update.verify_against_rules(rules):
            ret += update.middle_value

    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "47|53"), Rule(47, 53))
        self.assertEqual(load_line(0, "75,47,61,53,29"), Update([75, 47, 61, 53, 29]))
        self.assertEqual(load_line(0, ""), None)

    def test_update_middle_value(self):
        self.assertEqual(Update([75, 47, 61, 53, 29]).middle_value, 61)
        self.assertEqual(Update([75,29,13]).middle_value, 29)

    def test_update_verify_against_rules(self):
        update = Update([75, 47, 61, 53, 29])
        self.assertTrue(update.verify_against_rules([Rule(47, 53)]))
        self.assertFalse(update.verify_against_rules([Rule(53, 47)]))

    # def test_node(self):
    #     node = Node()
    #     node.merge_rule(Rule(47, 53))
    #     self.assertTrue(node.check_in_left(47))
    #     self.assertFalse(node.check_in_right(47))
    #     self.assertTrue(node.check_in_right(53))
    #     self.assertFalse(node.check_in_left(53))

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 143)

    def test_task(self):
        self.assertEqual(task(data_filename()), 5452)
