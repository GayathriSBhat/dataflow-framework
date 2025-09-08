from typing import Any, Dict
from ..observability.store import ObservabilityStore

def process(line_id: str, value: Dict[str, Any], store: ObservabilityStore) -> Dict[str, Any]:
    """
    Classify a parsed/enriched value.

    - If value['type'] == 'bad', we record the error (with payload) and mark label='unknown'
      instead of raising, so the pipeline can continue and the error is visible in /errors.
    - Otherwise, compute score -> label and trace the result.
    """
    processor_name = "classify"
    store.add_trace(line_id, processor_name, "start")
    with store.timed(processor_name):
        # Handle the known-bad case: record but don't raise
        if value.get("type") == "bad":
            exc = RuntimeError("unclassifiable type=bad")
            # record the error with payload for debugging
            try:
                store.record_error(processor_name, line_id, exc, payload=value)
            except TypeError:
                # backward-compatible: record_error may not accept payload
                store.record_error(processor_name, line_id, exc)
            # trace the error and return a safe fallback
            store.add_trace(line_id, processor_name, f"error:{repr(exc)}")
            value["label"] = "unknown"
            return value

        # Normal classification path
        score = float(value.get("score", 0.0))
        value["label"] = "error" if score > 0.9 else "ok"
        store.add_trace(line_id, processor_name, f"label={value['label']}")
        return value
