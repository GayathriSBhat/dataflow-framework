import importlib
import yaml


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def build_engine(config):
    from routing_engine.engine import RoutingEngine

    engine = RoutingEngine()
    for node in config["nodes"]:
        tag = node["tag"]
        module_path, class_name = node["type"].rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        engine.register(tag, cls())
    engine.validate()
    return engine
