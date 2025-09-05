from typing import Callable

# All processors must be functions: str -> str
ProcessorFn = Callable[[str], str]
