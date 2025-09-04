from processor_types import ProcessorFn

def run_pipeline(lines: list[str], processors: list[ProcessorFn]) -> list[str]:
    """Apply processors in sequence to all lines."""
    results = []
    for line in lines:
        for fn in processors:
            line = fn(line)
        results.append(line)
    return results
