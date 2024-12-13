from collections.abc import Generator, Callable, Iterator
from dataclasses import dataclass, field
from typing import Self, TextIO


@dataclass
class LineStream:
    iter: Iterator[str] = field(init=False)
    inx: int = field(init=False)

    @classmethod
    def from_string(cls, input: str) -> Self:
        lines = [l.strip() for l in input.strip().split("\n") if len(l) > 0]
        return cls(lines)

    @classmethod
    def from_text_file(cls, input: TextIO) -> Self:
        return cls(input.readlines())


    def __init__(self, input: list[str]):
        self.iter = iter(input)
        self.inx = 0

    def __iter__(self):
        return self

    def __next__(self):
        v = next(self.iter)
        self.inx += 1
        return v


def parse_lines[T](filename: str, line_parser: Callable[[int, str], T]) -> Generator[T]:
    with open(filename, 'r') as fp:
        i = 0
        for line in fp.readlines():
            yield line_parser(i, line)
            i += 1


def parse[T](filename: str, parser: Callable[[LineStream,], T]) -> Generator[T]:
    with open(filename, 'r') as fp:
        stream = LineStream.from_text_file(fp)
        while True:
            try:
                yield parser(stream)
            except StopIteration:
                break

