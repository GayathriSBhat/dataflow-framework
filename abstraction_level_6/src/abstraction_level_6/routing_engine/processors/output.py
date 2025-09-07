class TerminalOutput:
    emits = []

    def process(self, line):
        print(f"OUTPUT: {line}")
        return []
