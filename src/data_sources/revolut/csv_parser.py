from typing import Dict

from domain.transactions import Transaction


class CsvParser:
    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        raise NotImplementedError
