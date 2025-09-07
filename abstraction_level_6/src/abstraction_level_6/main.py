from routing_engine.config_loader import load_config, build_engine

if __name__ == "__main__":
    # Load config
    config = load_config("example_config.yaml")
    engine = build_engine(config)

    # Input lines
    input_lines = [
        "ERROR Disk failure",
        "WARN CPU high",
        "User logged in",
    ]

    # Run engine
    for tag, line in engine.run(input_lines):
        if tag == "end":
            print("Final:", line)
