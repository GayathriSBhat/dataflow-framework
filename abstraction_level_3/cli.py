import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Dynamic text processor")
    parser.add_argument("--input", required=True, help="Path to input file")
    parser.add_argument("--config", required=True, help="YAML pipeline config")
    parser.add_argument("--output", help="Optional output file")
    return parser.parse_args()
