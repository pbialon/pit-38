from typing import List

from domain.transactions import Transaction


class TransactionWithQuantity:
    def __init__(self, transaction: Transaction, quantity: float):
        self.transaction = transaction
        self.quantity = quantity

    def __init__(self, transaction: Transaction):
        self.transaction = transaction
        self.quantity = transaction.asset.amount

    def reduce_quantity(self, quantity: float):
        self.quantity -= quantity


class Queue:
    def __init__(self):
        self._queue: List[TransactionWithQuantity] = []

    def append(self, item: TransactionWithQuantity):
        self._queue.append(item)

    def head(self) -> TransactionWithQuantity:
        return self._queue[0]

    def head_quantity(self) -> float:
        return self.head().quantity

    def head_item(self):
        return self.head().transaction

    def pop_head(self):
        return self._queue.pop(0)

    def reduce_quantity_head(self, quantity: float):
        self._queue[0].reduce_quantity(quantity)
