class BasePostFilterBackend:
    def filter_entries(self, entries, feed):
        raise NotImplementedError("Subclasses must implement filter_entries()")
