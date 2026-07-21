class FakeSink:
    """Drop-in for tools.HttpSink that records instead of posting."""

    def __init__(self):
        self.items = []

    def collect(self, source, payload):
        self.items.append((source, payload))
