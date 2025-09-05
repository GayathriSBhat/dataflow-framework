"""Pipeline utilities: load processor functions and apply them in sequence."""
from pathlib import Path
from typing import List
import importlib
import yaml
from processor_types import ProcessorFn


def load_pipeline(config_path: Path) -> List[ProcessorFn]:
    """Load processor functions from a YAML pipeline config."""
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    steps = data["pipeline"]
    processors: List[ProcessorFn] = []
    for step in steps:
        module_path, func_name = step["type"].rsplit(".", 1)
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        processors.append(func)
    return processors


def apply_pipeline(lines: List[str], processors: List[ProcessorFn]) -> List[str]:
    """Apply a sequence of processors to each input line."""
    results: List[str] = []
    for line in lines:
        out = line
        for proc in processors:
            out = proc(out)
        results.append(out)
    return results
