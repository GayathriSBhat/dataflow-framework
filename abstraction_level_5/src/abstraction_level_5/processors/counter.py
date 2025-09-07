from typing import Iterator, Tuple

class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self, lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
        for line in lines:
            self.count += 1
            yield ("counted", f"[COUNT] {self.count}")
