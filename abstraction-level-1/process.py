# Usage: It processes text files to transform text into uppercase or snake_case.
'''This is a monolithic python script turned into a CLI app through Typer'''

import typer

'''What is dotenv?
>dotenv is a Python library that reads key-value pairs from a .env file and can set them as environment variables.
Why dotenv?
>Without it, Python won’t read .env automatically. You’d need to export variables manually in your shell'''

from dotenv import load_dotenv
import os

'''Relavance of typing (Type-checker)
If you accidentally tried to pass an int to transform_line(line: str, mode: str), a type checker could catch it.
'''
from typing import Iterator, Optional

app = typer.Typer()

# Load environment variables from .env
load_dotenv()

# step 2: Read lines from a file, stripping whitespace.
def read_lines(path: str) -> Iterator[str]:    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()

# Step 3: Function to convert text to uppercase or snake_case
def transform_line(line: str, mode: str) -> str:
    if mode == "uppercase":
        return line.upper()
    elif mode == "snakecase":
        return line.replace(" ", "_").lower()
    else:
        raise ValueError(f"Unsupported mode: {mode}")

# Step 4: Write processed lines either to a file or stdout.
def write_output(lines: Iterator[str], output_path: Optional[str]) -> None:    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    else:
        for line in lines:
            print(line)

''' define CLI options with the help of @app.command()'''
# Step 1: Define the command and its options
@app.command()
def process(
    input: str = typer.Option(..., "--input", "-i", help="Input file path"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    mode: Optional[str] = typer.Option(None, "--mode", "-m", help="Processing mode"),
):
   
    # Fallback to .env if mode not given
    if not mode:
        mode = os.getenv("MODE", "uppercase")


    # Lambda function to process each line
    lines = (transform_line(line, mode) for line in read_lines(input))
    write_output(lines, output)


if __name__ == "__main__":
    app()



''' How to pass input?
>Pass files via --input.
>Convert lines in a file to uppercase by default or using --mode uppercase.
>Convert lines in a file to snake_case if --mode snakecase is given.'''

''' How to get output?
>Writes to file if --output is given, or else prints in stdout.'''