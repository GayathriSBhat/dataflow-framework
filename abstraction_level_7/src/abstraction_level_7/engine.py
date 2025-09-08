import time
import threading
import uuid
from typing import Any, Optional
from .pipeline import PIPELINE
from .observability.store import Settings, ObservabilityStore
from .dashboard.server import start_dashboard_in_background

def process_line(line_id: str, raw_line: str, store: ObservabilityStore):
    """Process a single line through the pipeline"""
    if store.settings.enable_tracing:
        store.add_trace(line_id, "ingest", "ingested")

    value: Any = raw_line
    for proc in PIPELINE:
        # derive a friendly processor name:
        fn_name = getattr(proc, "__name__", "proc")
        proc_name = proc.__module__.split(".")[-1] if fn_name == "process" else fn_name

        try:
            value = proc(line_id, value, store)
        except Exception as exc:
            # Try to attach payload for more context when recording the error.
            # ObservabilityStore.record_error may accept payload (if you patched it).
            try:
                store.record_error(proc_name, line_id, exc, payload=value)
            except TypeError:
                # fallback if record_error signature hasn't been updated
                store.record_error(proc_name, line_id, exc)

            if store.settings.enable_tracing:
                store.add_trace(line_id, proc_name, f"error:{repr(exc)}")
            # stop processing this line
            return

    if store.settings.enable_tracing:
        store.add_trace(line_id, "complete", "completed")


def line_generator(rate_per_second: float):
    """Yield synthetic lines at approximately the requested rate."""
    import random

    delay = 1.0 / max(rate_per_second, 1.0)
    counter = 0
    while True:
        counter += 1
        if random.random() < 0.02:
            yield f"badline,missing_eq,{counter}"
        else:
            t = "good" if random.random() < 0.95 else "bad"
            yield f"id={counter},type={t},value={int(random.random()*100)}"
        time.sleep(delay)


def run_engine(settings: Settings):
    """Main orchestrator — starts dashboard and runs processing loop."""
    store = ObservabilityStore(settings)

    print(
        f"Starting dashboard on http://127.0.0.1:{settings.dashboard_port} "
        f"(tracing={'ON' if settings.enable_tracing else 'OFF'})"
    )
    start_dashboard_in_background(store, host="0.0.0.0", port=settings.dashboard_port)

    gen = line_generator(settings.rate)
    start_time = time.time()
    processed = 0
    try:
        for raw in gen:
            line_id = str(uuid.uuid4())
            process_line(line_id, raw, store)
            processed += 1
            # duration == 0 => run indefinitely
            if settings.duration > 0 and (time.time() - start_time) >= settings.duration:
                break
    except KeyboardInterrupt:
        print("Interrupted by user")

    print(f"Finished. Processed ~{processed} lines")
    # final snapshot
    snapshot = store.get_metrics_snapshot()
    for p, s in snapshot.items():
        avg = s["avg_time"]
        print(f"Processor {p}: count={s['count']} avg_time={avg:.6f}s errors={s['errors']}")
