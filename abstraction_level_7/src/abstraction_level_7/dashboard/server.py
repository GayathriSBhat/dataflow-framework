import threading
import uvicorn
import pathlib
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from ..observability.store import ObservabilityStore, Settings

# Create the FastAPI app first
app = FastAPI()

# Static files (index.html, app.js, styles.css) live in the `static` subfolder
static_dir = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Shared store will be mounted by the engine (start_dashboard_in_background)
_store: Optional[ObservabilityStore] = None


def mount_store(store: ObservabilityStore):
    """Attach the shared observability store so endpoints can use it."""
    global _store
    _store = store


@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the SPA index page."""
    index = static_dir / "index.html"
    return FileResponse(index)


@app.get("/stats")
def get_stats():
    if _store is None:
        return JSONResponse({"error": "store not mounted"}, status_code=500)
    return JSONResponse(_store.get_metrics_snapshot())


@app.get("/trace")
def get_traces(limit: int = 100):
    if _store is None:
        return JSONResponse({"error": "store not mounted"}, status_code=500)
    if not _store.settings.enable_tracing:
        return JSONResponse({"error": "tracing disabled"}, status_code=400)
    return JSONResponse(_store.get_traces(limit=limit))


@app.get("/errors")
def get_errors(limit: int = 100):
    if _store is None:
        return JSONResponse({"error": "store not mounted"}, status_code=500)
    return JSONResponse(_store.get_errors(limit=limit))


def _run_uvicorn(host: str, port: int):
    """Internal runner for uvicorn, executed in a background thread."""
    uvicorn.run(app, host=host, port=port, log_level="info")


def start_dashboard_in_background(
    store: ObservabilityStore, host: str = "0.0.0.0", port: int = 8000
):
    """Start the FastAPI dashboard in a daemon thread. Used by the engine."""
    mount_store(store)
    t = threading.Thread(
        target=_run_uvicorn, args=(host, port), daemon=True, name="dashboard-thread"
    )
    t.start()
    return t


# ---------------------------------------------------------------------
# Development helper: run this module directly to start a dev dashboard
# (mounts a temporary ObservabilityStore so endpoints return data).
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Dev settings; enable tracing so the UI can fetch /trace when you try it
    dev_settings = Settings(enable_tracing=True, traces_max=200, errors_max=200)
    dev_store = ObservabilityStore(dev_settings)
    mount_store(dev_store)

    # Run uvicorn in the foreground for convenience during development
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
