import typer
from .engine import run_engine
from .observability.store import Settings

app = typer.Typer(help="Observability Engine CLI")

@app.command()
def main(
    trace: bool = typer.Option(False, "--trace", help="Enable per-line tracing"),
    traces_max: int = typer.Option(1000, "--traces-max", help="Max number of traces to keep"),
    errors_max: int = typer.Option(500, "--errors-max", help="Max number of errors to keep"),
    rate: float = typer.Option(200.0, "--rate", help="Lines per second to simulate"),
    duration: float = typer.Option(10.0, "--duration", help="Run duration in seconds (0 = infinite)"),
    port: int = typer.Option(8000, "--port", help="Dashboard port (default 8000)"),
):

    """
    Run the processing engine with observability dashboard.
    Example:
      python -m observability_engine.cli main --trace --traces-max 2000 --errors-max 1000
    """
    settings = Settings(
        enable_tracing=trace,
        traces_max=traces_max,
        errors_max=errors_max,
        dashboard_port=port,
        rate=rate,
        duration=duration,
    )
    run_engine(settings)

if __name__ == "__main__":
    app()
