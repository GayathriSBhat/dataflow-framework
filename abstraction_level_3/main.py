''' read from input file, process lines through pipeline, write to output file or stdout '''

from cli import parse_args
from pipeline import load_pipeline
from core import run_pipeline

def main():
    args = parse_args()

    processors = load_pipeline(args.config)

    with open(args.input, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    results = run_pipeline(lines, processors)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
    else:
        for line in results:
            print(line)

if __name__ == "__main__":
    main()
