import csv
from typing import List

from loguru import logger

from data_sources.csv_parser import CsvParser
from domain.stock.operations.operation import Operation


class OperationsCsvReader:
    def __init__(self, path: str, csv_parser: CsvParser):
        self.path = path
        self.csv_parser = csv_parser

    def read(self) -> List[Operation]:
        operations = []
        logger.info(f"Reading operations from {self.path}...")
        with open(self.path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                operation = self.csv_parser.parse(row)
                if not operation:
                    continue

                operations.append(operation)
        logger.info(f"Parsed {len(operations)} operations")
        return operations
