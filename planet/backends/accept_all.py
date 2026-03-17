from planet.backends.base import BasePostFilterBackend


class AcceptAllBackend(BasePostFilterBackend):
    def filter_entries(self, entries, feed):
        return list(entries)
