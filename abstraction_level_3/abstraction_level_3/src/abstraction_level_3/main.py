"""Entry point: handles file read/write and delegates to CLI."""
from pathlib import Path
from typing import Optional
from core import process_text


def run(input: Path, config: Path, output: Optional[Path] = None) -> None:
    """Run the processing pipeline on the input file using the YAML config."""
    lines = input.read_text(encoding="utf-8").splitlines()
    results = process_text(lines, config)

    if output:
        output.write_text("\n".join(results) + "\n", encoding="utf-8")
    else:
        for line in results:
            print(line)


def main() -> None:
    from cli import app
    app()


if __name__ == "__main__":
    main()
