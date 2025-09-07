# cli.py
from __future__ import annotations

from pathlib import Path
from typing import Optional
import typer

app = typer.Typer(name="dag-pipeline", help="DAG-based log processing pipeline")


@app.command()
def run(
    config: Path = typer.Option(
        ...,
        "-c",
        "--config",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Pipeline YAML config file.",
    ),
    input: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Optional input file. If omitted, read from stdin (so you can pipe docker logs).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Optional output file (currently unused).",
    ),
) -> None:
    """Run the DAG pipeline."""
    # lazy import to avoid circular import at module import time
    from main import run as main_run
    main_run(input, config, output)


if __name__ == "__main__":
    app()
