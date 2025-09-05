"""Core orchestrator — the brains of the application.

This module exposes high-level functions to run the pipeline programmatically.
It does not perform file I/O or CLI parsing, so it can be reused in scripts, tests,
or other frontends (e.g., web API).
"""
from pathlib import Path
from typing import List
from pipeline import load_pipeline, apply_pipeline


def process_text(lines: List[str], config_path: Path) -> List[str]:
    """Process a list of input lines using the pipeline defined in a YAML config."""
    processors = load_pipeline(config_path)
    return apply_pipeline(lines, processors)


def process_line(line: str, config_path: Path) -> str:
    """Process a single line of text using the configured pipeline."""
    return process_text([line], config_path)[0]
