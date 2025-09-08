from typing import List, Callable, Any
from .processors import parse, enrich, classify, sink

# Each processor signature: (line_id: str, value: Any, store) -> Any
PIPELINE: List[Callable[[str, Any, object], Any]] = [
    parse.process,
    enrich.process,
    classify.process,
    sink.process,
]
