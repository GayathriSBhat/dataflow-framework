''' dynamically load and run processing pipeline from config '''
import importlib
import yaml
from processor_types import ProcessorFn

def load_pipeline(config_path: str) -> list[ProcessorFn]:
    """Load pipeline functions dynamically from YAML config."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    pipeline_fns: list[ProcessorFn] = []

    for step in config.get("pipeline", []):
        import_path = step["type"]
        module_name, func_name = import_path.rsplit(".", 1)

        try:
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Failed to load processor '{import_path}'. "
                f"Make sure the module and function exist."
            ) from e

        if not callable(func):
            raise TypeError(f"Processor '{import_path}' is not callable")

        pipeline_fns.append(func)

    return pipeline_fns
