from typing import Iterator, Tuple

def trim_processor(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    for line in lines:
        yield ("default", line.strip())
