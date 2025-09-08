import time
import random
from ..observability.store import ObservabilityStore

def process(line_id: str, value: dict, store: ObservabilityStore) -> dict:
    processor_name = "enrich"
    store.add_trace(line_id, processor_name, "start")
    with store.timed(processor_name):
        # simulate enrichment
        value["enriched_at"] = time.time()
        value["score"] = random.random()
        store.add_trace(line_id, processor_name, "enriched")
        return value
