import multiprocessing

import threading
from queue import Queue


class UniQueue(Queue):
    items = set()

    def put(self, item, block=True, timeout=None):
        if str(item) not in self.items:
            self.items.add(str(item))
            super().put(item, block, timeout)
