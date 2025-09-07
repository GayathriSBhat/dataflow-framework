# main.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator, Optional

from pipeline import load_pipeline_from_config
from core import run_dag


def read_input_lines(path: Optional[Path] = None) -> Iterator[str]:
    """Yield lines from a file if path provided, otherwise from stdin."""
    if path is None:
        try:
            for line in sys.stdin:
                yield line.rstrip("\n")
        except KeyboardInterrupt:
            return
    else:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                yield line.rstrip("\n")


def run(input: Optional[Path], config: Path, output: Optional[Path] = None) -> None:
    """Run the pipeline."""
    try:
        entry, nodes, routes = load_pipeline_from_config(str(config))
    except Exception as e:
        print(f"Failed to load pipeline config '{config}': {e}", file=sys.stderr)
        raise SystemExit(2) from e

    lines = read_input_lines(input)

    try:
        run_dag(entry, nodes, routes, lines)
    except KeyboardInterrupt:
        print("\nStopped by user", file=sys.stderr)
        raise SystemExit(0)
    except Exception as e:
        print(f"Pipeline execution failed: {e}", file=sys.stderr)
        raise SystemExit(3) from e


if __name__ == "__main__":
    from cli import app
    app()
