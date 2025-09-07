from typing import Iterator, Tuple

class Tally:
    def __init__(self):
        self.tally = 0

    def __call__(self, lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
        for line in lines:
            self.tally += 1
            yield ("tally", f"[TALLY] {self.tally}")
