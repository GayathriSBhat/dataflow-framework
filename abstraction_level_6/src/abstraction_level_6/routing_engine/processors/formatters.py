class SnakeCase:
    emits = ["end"]

    def process(self, line):
        formatted = line.replace(" ", "_").lower()
        yield ("end", formatted)
