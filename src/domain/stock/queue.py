from typing import List

from domain.transactions import Transaction


class Queue:
    def __init__(self):
        self._queue: List[(Transaction, float)] = []

    def append(self, item: Transaction, quantity: float):
        self._queue.append((item, quantity))

    def head_quantity(self) -> float:
        return self._queue[0][1]

    def head_item(self):
        return self._queue[0][0]

    def pop_head(self):
        return self._queue.pop(0)

    def reduce_quantity_head(self, quantity: float):
        item = self._queue[0][0]
        new_quantity = self._queue[0][1] - quantity
        self._queue[0] = (item, new_quantity)
