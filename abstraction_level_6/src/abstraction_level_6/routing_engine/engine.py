# routing_engine/engine.py
from collections import deque, Counter
import networkx as nx


class RoutingEngine:
    def __init__(self):
        # tag -> processor instance
        self.processors = {}
        # networkx graph of transitions (dynamic)
        self.graph = nx.DiGraph()
        # count transitions (tag_from, tag_to) -> count
        self.transition_counts = Counter()

    def register(self, tag, processor):
        """Register a processor under a tag."""
        self.processors[tag] = processor
        self.graph.add_node(tag)

    def validate(self):
        """Ensure every declared emitted tag maps to a processor (best-effort)."""
        missing = set()
        for tag, proc in self.processors.items():
            emits = getattr(proc, "emits", None)
            if emits:
                for out_tag in emits:
                    if out_tag not in self.processors:
                        missing.add(out_tag)
        if missing:
            raise ValueError(f"Unmapped tags in config: {missing}")

    def run(self, lines, max_steps=10000):
        """
        Run the routing engine from 'start' until 'end'.

        - lines: iterable of initial string lines
        - yields (tag, line) as lines reach 'end' or as they are processed if you want streaming
        """
        queue = deque([("start", line) for line in lines])
        steps = 0

        while queue:
            steps += 1
            if steps > max_steps:
                raise RuntimeError(
                    "Max steps exceeded — possible infinite loop. Increase max_steps or inspect graph."
                )

            tag, line = queue.popleft()

            # terminal
            if tag == "end":
                yield ("end", line)
                continue

            processor = self.processors.get(tag)
            if processor is None:
                raise ValueError(f"No processor registered for tag '{tag}'")

            # A processor.process may be a generator or return a list/iterator
            outputs = processor.process(line)
            for out in outputs:
                # outputs can be tuples (tag, line) OR yield nothing
                if out is None:
                    continue
                if not (isinstance(out, (list, tuple)) and len(out) == 2):
                    raise ValueError(
                        f"Processor {processor} must yield (tag, line) tuples, got: {out!r}"
                    )
                out_tag, out_line = out
                # record the transition
                self.transition_counts[(tag, out_tag)] += 1
                self.graph.add_edge(tag, out_tag)
                # save the edge attribute as count for later visualization
                self.graph[tag][out_tag]["count"] = self.transition_counts[(tag, out_tag)]
                queue.append((out_tag, out_line))
