from typing import Iterator, Tuple

def tag_lines(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    for line in lines:
        low = line.lower()
        if "error" in low:
            yield ("error", line)
        elif "warn" in low:
            yield ("warn", line)
        else:
            yield ("general", line)
