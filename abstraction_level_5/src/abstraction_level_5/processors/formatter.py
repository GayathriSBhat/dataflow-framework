from typing import Iterator, Tuple

def simple_formatter(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    for line in lines:
        formatted = f"[MSG] {line}"
        yield ("print", formatted)
