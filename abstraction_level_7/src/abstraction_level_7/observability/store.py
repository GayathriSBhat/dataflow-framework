"""
Thread-safe observability store providing:
 - metrics (count, total_time, errors)
 - traces (deque)
 - errors (deque)
 - context manager `timed(processor_name)` to measure durations

Settings are passed via the Settings dataclass.
"""

import logging
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Any, Deque, List, Optional

# logger for optional debug output
logger = logging.getLogger(__name__)

@dataclass
class Settings:
    enable_tracing: bool = False
    traces_max: int = 1000
    errors_max: int = 500
    dashboard_port: int = 8000
    rate: float = 200.0
    duration: float = 10.0

class ObservabilityStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        # locks
        self._metrics_lock = threading.Lock()
        self._trace_lock = threading.Lock()
        self._errors_lock = threading.Lock()

        # metrics_store: { processor_name: {"count": int, "total_time": float, "errors": int} }
        self._metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "total_time": 0.0, "errors": 0})

        # traces and errors
        self._traces: Deque[Dict[str, Any]] = deque(maxlen=settings.traces_max)
        self._errors: Deque[Dict[str, Any]] = deque(maxlen=settings.errors_max)

    # ---------------- metrics ----------------
    @contextmanager
    def timed(self, processor_name: str):
        """Context manager to time a processor execution and update metrics."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            with self._metrics_lock:
                self._metrics[processor_name]["count"] += 1
                self._metrics[processor_name]["total_time"] += elapsed

    def inc_error(self, processor_name: str):
        """Increment the error counter for a processor."""
        with self._metrics_lock:
            self._metrics[processor_name]["errors"] += 1

    def get_metrics_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return a snapshot of metrics with computed avg_time."""
        with self._metrics_lock:
            snapshot: Dict[str, Dict[str, Any]] = {}
            for k, v in self._metrics.items():
                cnt = v["count"]
                avg = (v["total_time"] / cnt) if cnt else 0.0
                snapshot[k] = {
                    "count": cnt,
                    "total_time": v["total_time"],
                    "avg_time": avg,
                    "errors": v["errors"],
                }
            return snapshot

    # ---------------- traces ----------------
    def add_trace(self, line_id: str, processor_name: str, note: str):
        """Add a trace step for a given line_id (if tracing enabled)."""
        if not self.settings.enable_tracing:
            return
        ts = time.time()
        with self._trace_lock:
            # append to existing trace if present
            for t in self._traces:
                if t.get("line_id") == line_id:
                    t["steps"].append((ts, processor_name, note))
                    return
            # create a new trace (most recent first)
            self._traces.appendleft({"line_id": line_id, "created": ts, "steps": [(ts, processor_name, note)]})

    def get_traces(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the most recent traces up to `limit` (newest first)."""
        if not self.settings.enable_tracing:
            return []
        with self._trace_lock:
            return list(self._traces)[:limit]

    # ---------------- errors ----------------
    def record_error(self, processor_name: str, line_id: str, exc: Exception, payload: Optional[Any] = None):
        """
        Record an error and optionally include the payload that caused it.

        The saved error dict includes:
          - timestamp
          - processor
          - line_id
          - error (repr)
          - payload (optional) - stored as-is or converted to string if not JSON-serializable

        Note: payload may be large; consider truncating/sanitizing before passing if needed.
        """
        # update metrics
        self.inc_error(processor_name)

        # build error record
        err: Dict[str, Any] = {
            "timestamp": time.time(),
            "processor": processor_name,
            "line_id": line_id,
            "error": repr(exc),
        }

        if payload is not None:
            try:
                # Try to store payload directly (usually small dicts are fine)
                err["payload"] = payload
            except Exception:
                # Fallback to string representation if direct storage fails
                try:
                    err["payload"] = str(payload)
                except Exception:
                    # Last resort: indicate payload couldn't be captured
                    err["payload"] = "<unserializable payload>"

        # optional logging for visibility in console
        try:
            logger.debug("Recording error: proc=%s line=%s err=%s", processor_name, line_id, repr(exc))
        except Exception:
            pass

        with self._errors_lock:
            self._errors.appendleft(err)

    def get_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return most recent error records up to `limit` (newest first)."""
        with self._errors_lock:
            return list(self._errors)[:limit]

    # ---------------- utility ----------------
    def clear_errors(self):
        """Dev helper: clear recent errors (not used in production)."""
        with self._errors_lock:
            self._errors.clear()

    def clear_traces(self):
        """Dev helper: clear traces (not used in production)."""
        with self._trace_lock:
            self._traces.clear()
