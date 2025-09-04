''' Tranformations applied on lines appear here'''

from typing import List
from processor_types import ProcessorFn

def to_uppercase(line: str) -> str:
    return line.upper()

def to_snakecase(line: str) -> str:
    line.replace(" ", "_").lower()

def apply_processors(line: str, processors: List[ProcessorFn]) -> str:
    for processor in processors:
        line = processor(line)
    return line
