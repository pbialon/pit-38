import copy
from typing import List

from domain.transactions import Transaction


class Queue:
    def __init__(self):
        self._queue: List[Transaction] = []

    def append(self, item: Transaction):
        copied = copy.deepcopy(item)
        self._queue.append(copied)

    def head(self) -> Transaction:
        try:
            return self._queue[0]
        except IndexError:
            raise IndexError("Queue is empty")

    def pop_head(self) -> Transaction:
        return self._queue.pop(0)

    def replace_head(self, new_item: Transaction):
        self._queue[0] = new_item

    def __repr__(self):
        return f"Queue({self._queue})"
