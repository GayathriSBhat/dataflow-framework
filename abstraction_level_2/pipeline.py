'''Converts mode passed through CLI  into a list called Processors'''

from core import to_uppercase, to_snakecase
from processor_types import ProcessorFn

def get_pipeline(mode: str) -> list[ProcessorFn]:
    if mode == "upper":
        return [to_uppercase]
    elif mode == "snake":
        return [to_snakecase]
    elif mode == "upper_snake":
        return [to_uppercase, to_snakecase]
    else:
        # Default: no transformation
        return []
