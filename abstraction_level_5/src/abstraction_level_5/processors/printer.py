from typing import Iterator, Tuple

def printer(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    for line in lines:
        print(line)
        continue
