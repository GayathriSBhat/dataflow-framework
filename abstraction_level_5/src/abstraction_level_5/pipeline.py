# pipeline.py
import importlib
from typing import Dict, Any, List
from dataclasses import dataclass

try:
    import yaml
except Exception as e:
    raise RuntimeError("PyYAML is required. Install with `pip install pyyaml`.") from e


@dataclass
class PipelineConfig:
    nodes: Dict[str, str]            # node_name -> import path
    routes: Dict[str, Dict[str, List[str]]]  # node_name -> (tag -> list of downstream node names)
    entry: str                       # starting node name


def load_yaml_config(path: str) -> PipelineConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict) or "pipeline" not in raw:
        raise ValueError("Invalid pipeline.yml: must contain top-level 'pipeline' mapping")

    pdata = raw["pipeline"]
    nodes = pdata.get("nodes", {})
    routes = pdata.get("routes", {})
    entry = pdata.get("entry")
    if entry is None:
        raise ValueError("pipeline.yml must specify an 'entry' node")

    return PipelineConfig(nodes=nodes, routes=routes, entry=entry)


def import_processor(path: str):
    """
    Import a callable from dotted path like "processors.trim.trim_processor".
    If the attribute is a class, try to instantiate it (no-arg constructor).
    Return a callable (function or callable instance).
    """
    if not isinstance(path, str):
        raise TypeError("processor path must be a string")
    parts = path.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid import path '{path}'. Use 'module.attr' form.")
    module_name, attr = parts
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        raise ImportError(f"Cannot import module '{module_name}' for processor '{path}': {e}") from e
    try:
        proc = getattr(module, attr)
    except AttributeError as e:
        raise ImportError(f"Module '{module_name}' has no attribute '{attr}' referenced by '{path}'") from e

    # If a class was referenced, instantiate it (expect no-arg constructor)
    if isinstance(proc, type):
        try:
            proc = proc()
        except Exception as e:
            raise ImportError(f"Failed to instantiate class '{path}': {e}") from e

    if not callable(proc):
        raise TypeError(f"Loaded object for node '{path}' is not callable")

    return proc


def load_pipeline_from_config(path: str):
    cfg = load_yaml_config(path)
    nodes = {}
    for name, import_path in cfg.nodes.items():
        proc = import_processor(import_path)
        nodes[name] = proc
    return cfg.entry, nodes, cfg.routes
