import argparse
import os.path
from datetime import date

def write_file(path: str, content: str):
    with open(path, "w") as fp:
        fp.write(content)


def generate(year: int, day: int):
    year_path = os.path.join(os.getcwd(), f"year{year}")
    if not os.path.exists(year_path):
        os.mkdir(year_path)

    day_path = os.path.join(year_path, f"day{day:02}")
    if not os.path.exists(day_path):
        os.mkdir(day_path)
    else:
        print(f"Directory for challenge {year}.{day} already exists")
        exit(1)

    write_file(os.path.join(day_path, "__init__.py"), "")
    write_file(os.path.join(day_path, "task1.txt"), "")
    write_file(os.path.join(day_path, "task1_example.txt"), "")
    write_file(os.path.join(day_path, "task2.txt"), "")
    write_file(os.path.join(day_path, "task2_example.txt"), "")
    code_content = """import unittest
from dataclasses import dataclass
from typing import Self

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse

@dataclass
class Row:
    value: int
    
    @classmethod
    def parse(cls, line: str) -> Self:
        separated = [int(v.strip()) for v in line.split(" ") if v != '']
        return cls(separated[0])


type LineModel = Row


def load_line(num: int, line: str) -> LineModel:
    return Row.parse(line)


def task(filename: str) -> int:
    ret = 0
    lines = parse(filename, load_line)
    for line in lines:
        pass
    return ret


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(load_line(0, ""), 0)

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 0)

    def test_task(self):
        self.assertEqual(task(data_filename()), 0)
"""
    write_file(os.path.join(day_path, "task1.py"), code_content)
    write_file(os.path.join(day_path, "task2.py"), code_content)

def main():
    parser = argparse.ArgumentParser(
        prog='bootstrap',
        description='Bootstrap an AoC daily challenge project')

    current_date = date.today()

    parser.add_argument('-y', '--year', type=int, default=current_date.year)
    parser.add_argument('-d', '--day', type=int, required=True)

    args = parser.parse_args()
    generate(args.year, args.day)


if __name__ == '__main__':
    main()
