import time
from typing import Any
from ..observability.store import ObservabilityStore

def process(line_id: str, value: str, store: ObservabilityStore) -> dict:
    processor_name = "parse"
    store.add_trace(line_id, processor_name, "start")
    with store.timed(processor_name):
        # naive parse
        parts = [p for p in value.strip().split(",") if p]
        data = {}
        for p in parts:
            if "=" not in p:
                raise ValueError(f"malformed token: {p}")
            k, v = p.split("=", 1)
            data[k.strip()] = v.strip()
        store.add_trace(line_id, processor_name, "parsed")
        return data
