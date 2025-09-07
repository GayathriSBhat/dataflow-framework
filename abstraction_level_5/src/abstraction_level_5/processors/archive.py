# processors/archive.py
from typing import Iterator, Tuple
from pathlib import Path
import os

def archive_errors(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    """
    Archive incoming lines to a file. Destination is controlled by the
    environment variable ARCHIVE_LOG_PATH. If not set, falls back to 'logs/archive.log'.

    IMPORTANT:
      - This function returns an iterator object (possibly empty). It does NOT
        forward lines downstream.
      - Returning `iter(())` ensures the DAG receives a valid iterable (not None).
    """
    # get destination from environment (no hardcoding required by user)
    dst = os.getenv("ARCHIVE_LOG_PATH")
    if not dst:
        # conservative fallback when env var not set
        dst = "logs/archive.log"

    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # perform the sink operation (write all incoming lines)
    with dst_path.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    # return an empty iterator to signal no downstream messages,
    # without relying on generator-function hacks.
    return iter(())
