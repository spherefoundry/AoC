import unittest
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
        new_files = []
        files = self.files.copy()
        empty = self.empty.copy()

        while len(empty) > 0:
            first_empty = empty.pop(0)
            last_file = files.pop()
            if first_empty.end > last_file.range.begin:
                files.append(last_file)
                continue
            if first_empty.len >= last_file.range.len:
                # copy whole file into the empty slot
                front, back = first_empty.split(last_file.range.len)
                new_files.append(File(last_file.id, front))
                if back.len > 0:
                    empty.insert(0, back)
            else:
                # take the whole empty slot
                front, back = last_file.range.split(first_empty.len)
                new_files.append(File(last_file.id, first_empty))
                if back.len > 0:
                    files.append(File(last_file.id, back.shift(-first_empty.len)))

        new_files.extend(files)
        new_files.sort(key=lambda a: a.range.begin)
        return Disk(new_files, [])

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

        # 00 99 8 111 888 2 777 333 6 44 6 5555 66
        expected = Disk(
            [
                File(0, Range(0, 2)),
                File(9, Range(2, 4)),
                File(8, Range(4, 5)),
                File(1, Range(5, 8)),
                File(8, Range(8, 11)),
                File(2, Range(11, 12)),
                File(7, Range(12, 15)),
                File(3, Range(15, 18)),
                File(6, Range(18, 19)),
                File(4, Range(19, 21)),
                File(6, Range(21, 22)),
                File(5, Range(22, 26)),
                File(6, Range(26, 27)),
                File(6, Range(27, 28))
            ],
            []
        )

        self.assertEqual(input.compact(), expected)

    def test_example(self):
        self.assertEqual(task(data_example_filename()), 1928)

    def test_task(self):
        self.assertEqual(task(data_filename()), 6359213660505)
