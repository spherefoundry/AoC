import unittest
from dataclasses import dataclass, field
from functools import cmp_to_key
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines


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

    def apply_rules(self, rules: list[Rule]) -> Self:
        def compare(left: int, right: int) -> int:
            for r in rules:
                if r.left == left and r.right == right:
                    return -1
                elif r.left == right and r.right == left:
                    return 1
            return 0

        sorted_pages = sorted(self.pages, key=cmp_to_key(compare))

        return Update(sorted_pages)


type LineModel = Rule | Update | None


def load_line(num: int, line: str) -> LineModel:
    if (rule := Rule.parse(line)) is not None:
        return rule
    if (update := Update.parse(line)) is not None:
        return update
    return None


def task(filename: str) -> int:
    ret = 0
    lines = parse_lines(filename, load_line)

    rules: list[Rule] = []
    updates: list[Update] = []
    for line in lines:
        if type(line) is Rule:
            rules.append(line)
        if type(line) is Update:
            updates.append(line)

    for update in updates:
        if update.verify_against_rules(rules):
            continue
        improved_update = update.apply_rules(rules)
        ret += improved_update.middle_value

    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, "47|53"), Rule(47, 53))
        self.assertEqual(load_line(0, "75,47,61,53,29"), Update([75, 47, 61, 53, 29]))
        self.assertEqual(load_line(0, ""), None)

    def test_update_middle_value(self):
        self.assertEqual(Update([75, 47, 61, 53, 29]).middle_value, 61)
        self.assertEqual(Update([75, 29, 13]).middle_value, 29)

    def test_update_verify_against_rules(self):
        update = Update([75, 47, 61, 53, 29])
        self.assertTrue(update.verify_against_rules([Rule(47, 53)]))
        self.assertFalse(update.verify_against_rules([Rule(53, 47)]))

    def test_update_apply_rules(self):
        self.assertEqual(Update([75, 47, 61, 53, 29]).apply_rules([Rule(47, 53)]), Update([75, 47, 61, 53, 29]))

        rules = [
            Rule(47, 53),
            Rule(97, 13),
            Rule(97, 61),
            Rule(97, 47),
            Rule(75, 29),
            Rule(61, 13),
            Rule(75, 53),
            Rule(29, 13),
            Rule(97, 29),
            Rule(53, 29),
            Rule(61, 53),
            Rule(97, 53),
            Rule(61, 29),
            Rule(47, 13),
            Rule(75, 47),
            Rule(97, 75),
            Rule(47, 61),
            Rule(75, 61),
            Rule(47, 29),
            Rule(75, 13),
            Rule(53, 13)
        ]
        self.assertEqual(Update([75, 97, 47, 61, 53]).apply_rules(rules), Update([97, 75, 47, 61, 53]))
        self.assertEqual(Update([61, 13, 29]).apply_rules(rules), Update([61, 29, 13]))
        self.assertEqual(Update([97, 13, 75, 29, 47]).apply_rules(rules), Update([97, 75, 47, 29, 13]))

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 123)

    def test_task(self):
        self.assertEqual(task(data_filename()), 4598)
