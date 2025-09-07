class OnlyError:
    emits = ["end"]

    def process(self, line):
        if "ERROR" in line:
            yield ("end", f"[ERROR]: {line}")


class OnlyWarn:
    emits = ["end"]

    def process(self, line):
        if "WARN" in line:
            yield ("end", f"[WARN]: {line}")
