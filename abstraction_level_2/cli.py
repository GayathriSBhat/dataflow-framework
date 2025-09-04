'''Implements CLI using typer and calls functions to rw files '''

import typer
from main import process_file
from typing import Optional


app = typer.Typer()

@app.command()
def main( input: str = typer.Option(..., "--input", "-i", help="Input file path"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    mode: Optional[str] = typer.Option(None, "--mode", "-m", help="Processing mode"),):    
    process_file(input, output, mode)


if __name__ == "__main__":
    app()
