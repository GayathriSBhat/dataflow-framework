# core.py
from typing import Dict, List, Iterator
from collections import deque

from processor_types import ProcessorFn  # type: ignore  # ProcessorFn = Callable[[Iterator[str]], Iterator[Tuple[str, str]]]


def run_dag(entry: str,
            nodes: Dict[str, ProcessorFn],
            routes: Dict[str, Dict[str, List[str]]],
            initial_lines: Iterator[str]) -> None:
    """
    Simple DAG engine:
     - nodes: mapping name -> processor callable (Iterator[str] -> Iterator[(tag, line)])
     - routes: mapping node -> (tag -> list of downstream node names)
     - entry: starting node name
     - initial_lines: iterator of raw input strings
    """
    if entry not in nodes:
        raise ValueError(f"Entry node '{entry}' not present among nodes {list(nodes)}")

    # buffers: node_name -> deque of lines (strings)
    buffers: Dict[str, deque] = {name: deque() for name in nodes.keys()}

    # seed entry buffer
    for line in initial_lines:
        buffers[entry].append(line)

    # process until all buffers empty
    while True:
        # find a node with data
        ready = next((n for n, q in buffers.items() if q), None)
        if ready is None:
            break  # all empty

        # drain the buffer into an iterator for the processor
        q = buffers[ready]

        def iter_and_clear(dq: deque):
            while dq:
                yield dq.popleft()

        proc = nodes[ready]
        try:
            outputs = proc(iter_and_clear(q))
        except Exception as e:
            # Propagate with context
            raise RuntimeError(f"Error while running processor '{ready}': {e}") from e

        # DEFENSIVE: if processor returned None, treat as no outputs (sink)
        if outputs is None:
            # nothing to route from this processor
            continue

        # DEFENSIVE: ensure outputs is iterable
        try:
            iter(outputs)
        except TypeError:
            raise RuntimeError(f"Processor '{ready}' returned a non-iterable ({type(outputs)!r}). "
                               "Processors must return an iterator of (tag, payload) pairs.")

        # route outputs
        node_routes = routes.get(ready, {})
        for tag, payload in outputs:
            # find downstream node names for this tag; allow default fallback
            targets = node_routes.get(tag)
            if targets is None:
                targets = node_routes.get("default", [])
            if not targets:
                # no downstream targets: drop
                continue
            for t in targets:
                if t not in buffers:
                    raise ValueError(f"Route target '{t}' not known (from node {ready})")
                buffers[t].append(payload)
