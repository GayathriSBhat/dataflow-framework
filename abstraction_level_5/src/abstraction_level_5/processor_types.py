# processor_types.py
from typing import Iterator, Tuple, Callable

# A tagged line: (tag, line)
TaggedLine = Tuple[str, str]

# Processor type: consumes an iterator of raw strings and yields tagged lines.
ProcessorFn = Callable[[Iterator[str]], Iterator[TaggedLine]]
