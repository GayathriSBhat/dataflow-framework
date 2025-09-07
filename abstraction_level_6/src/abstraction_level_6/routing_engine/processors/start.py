class StartProcessor:
    """Entry processor: tags lines as 'error', 'warn', or 'general'."""
    emits = ["error", "warn", "general"]

    def process(self, line):
        if "ERROR" in line:
            yield ("error", line)
        elif "WARN" in line:
            yield ("warn", line)
        else:
            yield ("general", line)
