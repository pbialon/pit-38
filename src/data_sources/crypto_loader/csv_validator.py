import csv
from dataclasses import dataclass
from typing import List, Set
import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import Currency
from domain.transactions import Action


@dataclass
class ValidationError:
    row_number: int
    column: str
    value: str
    reason: str

    def __str__(self):
        return f"Row {self.row_number}: Invalid value '{self.value}' in column '{self.column}'. {self.reason}"


class CsvValidator:
    REQUIRED_COLUMNS = {"date", "operation", "amount", "symbol", "fiat_value", "currency"}
    VALID_OPERATIONS = {action.value for action in Action}
    VALID_CURRENCIES = {currency.value for currency in Currency}

    @classmethod
    def validate(cls, file_path: str) -> List[ValidationError]:
        """
        Validate CSV file format and data.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of validation errors. Empty list means the file is valid.
        """
        errors = []
        
        try:
            with open(file_path, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate columns
                column_errors = cls._validate_columns(set(reader.fieldnames or []))
                if column_errors:
                    errors.extend(column_errors)
                    logger.warning(f"Invalid CSV format in {file_path}: {column_errors}")
                    return errors
                
                # Validate rows
                for row_number, row in enumerate(reader, start=1):
                    row_errors = cls._validate_row(row_number, row)
                    errors.extend(row_errors)
                    
            if errors:
                logger.warning(f"Found {len(errors)} validation errors in {file_path}")
            else:
                logger.debug(f"CSV file {file_path} is valid")
                
        except Exception as e:
            logger.error(f"Failed to validate CSV file {file_path}: {str(e)}")
            errors.append(ValidationError(0, "", "", f"Failed to read CSV file: {str(e)}"))
            
        return errors

    @classmethod
    def _validate_columns(cls, columns: Set[str]) -> List[ValidationError]:
        errors = []
        missing_columns = cls.REQUIRED_COLUMNS - columns
        
        if missing_columns:
            errors.append(
                ValidationError(
                    row_number=0,
                    column="",
                    value="",
                    reason=f"Missing required columns: {', '.join(missing_columns)}"
                )
            )
        
        return errors

    @classmethod
    def _validate_row(cls, row_number: int, row: dict) -> List[ValidationError]:
        errors = []
        
        # Validate date format
        try:
            pendulum.parse(row["date"])
        except ValueError as e:
            errors.append(
                ValidationError(
                    row_number=row_number,
                    column="date",
                    value=row["date"],
                    reason="Invalid date format"
                )
            )
        
        # Validate operation
        operation = row["operation"]
        if operation not in cls.VALID_OPERATIONS:
            errors.append(
                ValidationError(
                    row_number=row_number,
                    column="operation",
                    value=operation,
                    reason=f"Operation must be one of: {', '.join(cls.VALID_OPERATIONS)}"
                )
            )
        
        # Validate amount
        try:
            amount = float(row["amount"])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError as e:
            errors.append(
                ValidationError(
                    row_number=row_number,
                    column="amount",
                    value=row["amount"],
                    reason=str(e)
                )
            )
        
        # Validate symbol
        symbol = row["symbol"]
        if not symbol:
            errors.append(
                ValidationError(
                    row_number=row_number,
                    column="symbol",
                    value=symbol,
                    reason="Symbol cannot be empty"
                )
            )
        
        # Validate fiat_value
        try:
            fiat_value = float(row["fiat_value"])
            if fiat_value < 0:
                raise ValueError("Fiat value cannot be negative")
        except ValueError as e:
            errors.append(
                ValidationError(
                    row_number=row_number,
                    column="fiat_value",
                    value=row["fiat_value"],
                    reason=str(e)
                )
            )
        
        # Validate currency
        currency = row["currency"]
        if currency not in cls.VALID_CURRENCIES:
            errors.append(
                ValidationError(
                    row_number=row_number,
                    column="currency",
                    value=currency,
                    reason=f"Currency must be one of: {', '.join(cls.VALID_CURRENCIES)}"
                )
            )
        
        return errors 