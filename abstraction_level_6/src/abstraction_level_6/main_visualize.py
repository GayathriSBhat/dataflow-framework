# main_visualize.py
from routing_engine.config_loader import load_config, build_engine
from routing_engine.visualize import visualize_graph

if __name__ == "__main__":
    config = load_config("example_config.yaml")
    engine = build_engine(config)

    # Example input lines
    input_lines = [
        "ERROR Disk failure",
        "ERROR Disk failure",  # duplicate to show heavier edge counts
        "WARN CPU high",
        "User logged in",
        "User logged in",
        "User logged in"
    ]

    # Run engine (this populates engine.graph and transition_counts)
    for tag, line in engine.run(input_lines):
        if tag == "end":
            # optionally inspect final/output lines here
            print("FINAL:", line)

    # Visualize and save
    visualize_graph(engine, show=True, filename="routing_graph.png")
