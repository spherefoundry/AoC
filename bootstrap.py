import argparse
import os.path
import shutil
from datetime import date
from urllib.error import URLError, HTTPError


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

    print(f"Generating challenge project for {year}.{day}")

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
    print(f"Done!")


def download(year: int, day: int, session: str):
    day_path = os.path.join(os.getcwd(), f"year{year}", f"day{day:02}")
    if not os.path.exists(day_path):
        print(f"Directory for challenge {year}.{day} doesn't exists. Generate first.")
        exit(1)

    print(f"Downloading challenge input for project {year}.{day}")

    import urllib.request
    req = urllib.request.Request(method='GET', url=f'https://adventofcode.com/{year}/day/{day}/input')
    req.add_header("Cookie", f"session={session}")
    try:
        with urllib.request.urlopen(req) as f:
            if f.status == 404:
                print(f"The file is not available yet.")
                exit(1)
            write_file(os.path.join(day_path, "task1.txt"), f.read().decode('utf-8'))
            shutil.copy(os.path.join(day_path, "task1.txt"), os.path.join(day_path, "task2.txt"))
    except HTTPError as e:
        if e.code == 404:
            print(f"The file is not available yet.")
            exit(1)
        else:
            print(f"There was a problem {e.code} downloading the file: {e.reason}")
            exit(1)
    except URLError as e:
        print(f"There was a problem downloading the file: {e.reason}")

    print(f"Done!")


def main():
    parser = argparse.ArgumentParser(
        prog='bootstrap',
        description='Bootstrap an AoC daily challenge project')

    current_date = date.today()

    parser.add_argument('-y', '--year', type=int, default=current_date.year)
    parser.add_argument('-d', '--day', type=int, required=True)

    subparsers = parser.add_subparsers(dest='command', required=True, help="Commands")

    parser_generate = subparsers.add_parser("generate", help="Generate an AoC challenge project")
    parser_download = subparsers.add_parser("download", help="Download an AoC challenge input")
    parser_download.add_argument('-s', '--session', type=str, required=True)
    parser_full = subparsers.add_parser("full", help="Perform all commands for an AoC challenge")
    parser_full.add_argument('-s', '--session', type=str, required=True)

    args = parser.parse_args()

    match args.command:
        case "generate":
            generate(args.year, args.day)
        case "download":
            download(args.year, args.day, args.session)
        case "full":
            generate(args.year, args.day)
            download(args.year, args.day, args.session)


if __name__ == '__main__':
    main()
