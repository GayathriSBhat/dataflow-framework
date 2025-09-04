'''Reads input file, writes into  output file'''

from pipeline import get_pipeline
from core import apply_processors

def process_file(input_path: str, output_path: str, mode: str):
    processors = get_pipeline(mode)
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    processed_lines = [apply_processors(line.rstrip("\n"), processors) for line in lines]

    with open(output_path, "w", encoding="utf-8") as outfile:
        for line in processed_lines:
            outfile.write(line + "\n")
