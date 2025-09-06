"""
Level 4 – Stream Processing and State
------------------------------------------
This module defines a simple stream processing framework where processors
operate on streams of lines (Iterator[str] -> Iterator[str]).

Features:
- Adapter for old str -> str processors
- Stateless and stateful stream processors
- Fan-out (Splitter), Fan-in (PairJoiner)
- Stateful processors (LineCounter, MinLengthFilter)
- Pipeline runner to chain processors
- Demo usage
"""

# ============================================================
# Imports
# ============================================================
from typing import Iterator, Callable, Protocol, Iterable, List, Optional
from dataclasses import dataclass, field


# ============================================================
# Processor Interface
# ============================================================
class StreamProcessor(Protocol):
    """A stream processor consumes an iterator of strings and yields strings."""

    def __call__(self, lines: Iterator[str]) -> Iterator[str]:
        ...


# ============================================================
# Adapter for old str -> str processors
# ============================================================
def wrap_str_to_str(func: Callable[[str], str]) -> Callable[[Iterator[str]], Iterator[str]]:
    """
    Wrap a simple str->str function into a stream-aware processor.
    Returns an Iterator[str] for compatibility with stream pipelines.
    """
    def processor(lines: Iterator[str]) -> Iterator[str]:
        for line in lines:
            out = func(line)
            if out is None:
                continue
            yield out
    return processor


# ============================================================
# Example Processors
# ============================================================
@dataclass
class LineCounter:
    """Stateful: prefixes each line with a running counter."""
    start: int = 0

    def __call__(self, lines: Iterator[str]) -> Iterator[str]:
        count = self.start
        for line in lines:
            count += 1
            yield f"{count}\t{line}"


@dataclass
class PairJoiner:
    """Fan-in: joins every two lines together into one."""
    sep: str = " | "
    emit_leftover: bool = True

    def __call__(self, lines: Iterator[str]) -> Iterator[str]:
        it = iter(lines)
        while True:
            try:
                a = next(it)
            except StopIteration:
                break
            try:
                b = next(it)
                yield f"{a}{self.sep}{b}"
            except StopIteration:
                if self.emit_leftover:
                    yield a
                break


@dataclass
class Splitter:
    """Fan-out: splits each line into multiple lines on a delimiter."""
    delim: str = ","
    maxsplit: int = -1

    def __call__(self, lines: Iterator[str]) -> Iterator[str]:
        for line in lines:
            parts = line.split(self.delim, self.maxsplit if self.maxsplit != -1 else -1)
            for p in parts:
                yield p


@dataclass
class MinLengthFilter:
    """Configurable: only passes lines with length >= min_length."""
    min_length: int = 1
    dropped_count: int = field(default=0, init=False)

    def __call__(self, lines: Iterator[str]) -> Iterator[str]:
        for line in lines:
            if len(line) >= self.min_length:
                yield line
            else:
                self.dropped_count += 1

    assert output == ["abc", "abcd"]     # only lines length >= 3 survive
    assert mf.dropped_count == 2   


# ============================================================
# Pipeline Runner
# ============================================================
def run_pipeline(initial_lines: Iterable[str], processors: List[StreamProcessor]) -> Iterator[str]:
    """Chain processors: each consumes the output of the previous."""
    iterator: Iterator[str] = iter(initial_lines)
    for proc in processors:
        iterator = proc(iterator)
    return iterator


# ============================================================
# Example: Reusing Old str->str Processor
# ============================================================
def uppercase_line(line: str) -> Optional[str]:
    """Old-style processor: converts to uppercase, drops empty lines."""
    s = line.strip()
    return s.upper() if s else None

# Wrapped into a stream processor
uppercase_processor = wrap_str_to_str(uppercase_line)


# ============================================================
# Demo / Quick Tests
# ============================================================
def demo():
    raw = [
        "hello,world",
        "foo,bar,baz",
        "",
        "last,line"
    ]

    processors = [
        Splitter(delim=","),
        uppercase_processor,
        MinLengthFilter(min_length=3),
        LineCounter(start=0),
    ]

    out = list(run_pipeline(raw, processors))
    print("Pipeline output (split -> upper -> filter -> count):")
    for o in out:
        print(repr(o))

    print("\nPairJoiner output:")
    raw2 = ["one", "two", "three", "four", "five"]
    out2 = list(run_pipeline(raw2, [PairJoiner(sep=" + ")]))
    for o in out2:
        print(repr(o))

    print("\nMinLengthFilter output + dropped count:")
    mf = MinLengthFilter(min_length=4)
    out3 = list(run_pipeline(["a", "abcd", "xyz", "12345"], [mf]))
    print(out3, "| Dropped:", mf.dropped_count)


# ============================================================
# Main Entry
# ============================================================
if __name__ == "__main__":
    demo()

  