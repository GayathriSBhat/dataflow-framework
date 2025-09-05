"""Command-line interface using Typer."""
from pathlib import Path
from typing import Optional
import typer
import main as main_module

app = typer.Typer()


@app.command()
def run(
    input: Path = typer.Option(..., "-i", "--input", exists=True, file_okay=True, dir_okay=False, readable=True),
    config: Path = typer.Option(..., "-c", "--config", exists=True, file_okay=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
) -> None:
    """CLI command to invoke the main pipeline run."""
    main_module.run(input, config, output)
