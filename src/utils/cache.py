from time import time


class TimedCache:
    def __init__(self, expire: int = 15):
        self.items = {}
        self.expire = expire

    def __setitem__(self, key, value):
        self.items[key] = {
            "value": value,
            "time": time(),
        }

    def __getitem__(self, key):
        item = self.items.get(key)

        if not item:
            return None

        if item["time"] + self.expire < time():
            return None

        return item["value"]

    def __delitem__(self, key):
        del self.items[key]
