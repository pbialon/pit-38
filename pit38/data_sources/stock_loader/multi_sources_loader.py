from typing import List
from loguru import logger

from pit38.domain.stock.operations.operation import Operation
from pit38.domain.transactions.transaction import Transaction
from pit38.data_sources.stock_loader.csv_loader import Loader


class MultiSourcesLoader:
    def __init__(self, loader: Loader):
        self.loader = loader

    def load(self, file_paths: List[str]) -> List[Operation | Transaction]:
        all_operations = []
        
        for file_path in file_paths:
            try:
                operations = self.loader.load(file_path)
                all_operations.extend(operations)
                logger.info(f"Successfully loaded {len(operations)} operations from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load operations from {file_path}: {str(e)}")
                raise e
        
        sorted_operations = sorted(all_operations, key=lambda op: op.date)
        logger.info(f"Total operations loaded: {len(sorted_operations)}")
        
        return sorted_operations 