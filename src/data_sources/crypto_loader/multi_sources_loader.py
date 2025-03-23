from typing import List
from loguru import logger

from domain.transactions import Transaction
from data_sources.crypto_loader.csv_loader import Loader


class MultiSourcesLoader:
    def __init__(self, loader: Loader):
        self.loader = loader

    def load(self, file_paths: List[str]) -> List[Transaction]:
        """
        Load transactions from multiple CSV files, merge and sort them by date
        
        Args:
            file_paths: List of paths to CSV files containing transactions
            
        Returns:
            List of transactions sorted by date
        """
        all_transactions = []
        
        for file_path in file_paths:
            try:
                transactions = self.loader.load(file_path)
                all_transactions.extend(transactions)
                logger.info(f"Successfully loaded {len(transactions)} transactions from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load transactions from {file_path}: {str(e)}")
                continue
        
        sorted_transactions = sorted(all_transactions, key=lambda t: t.date)
        logger.info(f"Total transactions loaded: {len(sorted_transactions)}")
        
        return sorted_transactions
