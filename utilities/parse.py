from collections.abc import Generator, Callable


def parse[T](filename: str, line_parser: Callable[[int, str], T]) -> Generator[T]:
    with open(filename, 'r') as fp:
        i = 0
        for line in fp.readlines():
            yield line_parser(i, line)
            i += 1
