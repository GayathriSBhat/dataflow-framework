import time
import random
from ..observability.store import ObservabilityStore

def process(line_id: str, value: dict, store: ObservabilityStore) -> dict:
    processor_name = "sink"
    store.add_trace(line_id, processor_name, "start")
    with store.timed(processor_name):
        # simulate occasional slowness
        if random.random() < 0.01:
            time.sleep(0.05)
        else:
            time.sleep(random.uniform(0.0005, 0.002))
        store.add_trace(line_id, processor_name, "emitted")
        return value
