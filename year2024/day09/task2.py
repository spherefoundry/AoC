import unittest
from bisect import insort
from dataclasses import dataclass
from typing import Self, Tuple

from utilities.file import data_example_filename, data_filename
from utilities.parse import parse_lines


@dataclass(frozen=True)
class Range:
    begin: int
    end: int

    @property
    def len(self) -> int:
        return self.end - self.begin

    def split(self, after: int) -> Tuple[Self, Self]:
        assert after >= 0
        assert after <= self.len

        return Range(self.begin, self.begin + after), Range(self.begin + after, self.end)

    def shift(self, by: int) -> Self:
        return Range(self.begin + by, self.end + by)


@dataclass(frozen=True)
class File:
    id: int
    range: Range


@dataclass(frozen=True)
class Disk:
    files: list[File]
    empty: list[Range]

    @classmethod
    def parse(cls, line: str) -> Self:
        file_ranges = []
        empty_ranges = []
        is_file = True
        file_id = 0
        position = 0
        for ch in line.strip():
            len = int(ch)
            if len != 0:
                range = Range(position, position + len)
                position += len

                if is_file:
                    file_ranges.append(File(file_id, range))
                    file_id += 1
                else:
                    empty_ranges.append(range)

            is_file = not is_file

        return cls(file_ranges, empty_ranges)

    def compact(self) -> Self:
        # 00...111...2...333.44.5555.6666.777.888899
        # 00992111777.44.333....5555.6666.....8888..

        new_files = []
        files = self.files.copy()
        files.reverse()
        empty = self.empty.copy()

        for file in files:
            for i in range(len(empty)):
                candidate = empty[i]
                if candidate.begin > file.range.begin:
                    continue
                if candidate.len >= file.range.len:
                    # move the file
                    front, back = candidate.split(file.range.len)
                    new_files.append(File(file.id, front))
                    insort(empty, file.range, key=lambda a: a.begin)
                    if back.len > 0:
                        empty[i] = back
                    else:
                        del empty[i]
                    break
            else:
                # keep it as is
                new_files.append(file)

        new_files.sort(key=lambda a: a.range.begin)
        empty.sort(key=lambda a: a.begin)
        return Disk(new_files, empty)

    @property
    def checksum(self) -> int:
        ret = 0
        for file in self.files:
            for i in range(file.range.begin, file.range.end):
               ret += file.id * i

        return ret


type LineModel = Disk


def load_line(num: int, line: str) -> LineModel:
    return Disk.parse(line)


def task(filename: str) -> int:
    disks = list(parse_lines(filename, load_line))
    assert len(disks) == 1
    return disks[0].compact().checksum


class TestCases(unittest.TestCase):
    def test_load_line(self):
        self.assertEqual(
            load_line(0, "90909"),
            Disk(
                [File(0, Range(0, 9)), File(1, Range(9, 18)), File(2, Range(18, 27))],
                []
            )
        )
        # 00...111...2...333.44.5555.6666.777.888899
        self.assertEqual(
            load_line(0, "2333133121414131402"),
            Disk(
                [
                    File(0, Range(0, 2)),
                    File(1, Range(5, 8)),
                    File(2, Range(11, 12)),
                    File(3, Range(15, 18)),
                    File(4, Range(19, 21)),
                    File(5, Range(22, 26)),
                    File(6, Range(27, 31)),
                    File(7, Range(32, 35)),
                    File(8, Range(36, 40)),
                    File(9, Range(40, 42)),
                ],
                [
                    Range(2, 5),
                    Range(8, 11),
                    Range(12, 15),
                    Range(18, 19),
                    Range(21, 22),
                    Range(26, 27),
                    Range(31, 32),
                    Range(35, 36),
                ]
            )
        )

    def test_disk_compact(self):
        input = Disk(
            [
                File(0, Range(0, 2)),
                File(1, Range(5, 8)),
                File(2, Range(11, 12)),
                File(3, Range(15, 18)),
                File(4, Range(19, 21)),
                File(5, Range(22, 26)),
                File(6, Range(27, 31)),
                File(7, Range(32, 35)),
                File(8, Range(36, 40)),
                File(9, Range(40, 42)),
            ],
            [
                Range(2, 5),
                Range(8, 11),
                Range(12, 15),
                Range(18, 19),
                Range(21, 22),
                Range(26, 27),
                Range(31, 32),
                Range(35, 36),
            ]
        )

        # 00992111777.44.333....5555.6666.....8888..
        expected = Disk(
            [
                File(0, Range(0, 2)),
                File(9, Range(2, 4)),
                File(2, Range(4, 5)),
                File(1, Range(5, 8)),
                File(7, Range(8, 11)),
                File(4, Range(12, 14)),
                File(3, Range(15, 18)),
                File(5, Range(22, 26)),
                File(6, Range(27, 31)),
                File(8, Range(36, 40)),
            ],
            [
                Range(begin=11, end=12),
                Range(begin=14, end=15),
                Range(begin=18, end=19),
                Range(begin=19, end=21),
                Range(begin=21, end=22),
                Range(begin=26, end=27),
                Range(begin=31, end=32),
                Range(begin=32, end=35),
                Range(begin=35, end=36),
                Range(begin=40, end=42),
            ]
        )

        self.assertEqual(input.compact(), expected)

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 2858)

    def test_task(self):
        self.assertEqual(task(data_filename()), 6381624803796)
