# PIT-38 — Polish Investment Tax Calculator

## Project Overview

CLI tool for calculating Polish income tax on stocks and cryptocurrency (PIT-38 form).
Supports importing transaction data from multiple brokers (Revolut, E*Trade, Binance),
converting foreign currencies to PLN using NBP (National Bank of Poland) exchange rates,
and computing tax liability at the 19% flat rate.

## Quick Reference

```bash
# Run stock tax calculation
PYTHONPATH=./src python -m stock -f <file1> -f <file2> -y 2025

# Run crypto tax calculation
PYTHONPATH=./src python -m crypto -f <file1> -y 2025

# Import from broker (Revolut stocks example)
PYTHONPATH=./src python -m plugins.stock.revolut --input-path <export> --output-path <output>

# Run tests
PYTHONPATH=./src python -m unittest discover tests

# Run a single test file
PYTHONPATH=./src python -m pytest tests/test_profit_calculator.py
```

## Architecture

```
src/
├── stock.py / crypto.py        # CLI entry points (Click commands)
├── exchanger.py                # Factory for currency exchanger
├── plugins/                    # Broker-specific importers
│   ├── stock/                  #   Revolut, E*Trade → standardized CSV
│   └── crypto/                 #   Revolut, Binance → standardized CSV
├── data_sources/               # Generic CSV loaders for standardized format
│   ├── stock_loader/
│   └── crypto_loader/
└── domain/                     # Core business logic
    ├── transactions/           #   Transaction, Action (BUY/SELL), AssetValue
    ├── stock/                  #   Stock operations, FIFO profit calc, stock splits
    │   ├── operations/         #     Dividend, ServiceFee, StockSplit, Operation
    │   └── profit/             #     ProfitCalculator, PerStockCalculator, StockSplitHandler
    ├── crypto/                 #   Crypto profit calculator
    ├── currency_exchange_service/  # NBP API rates, Currency/FiatValue types
    ├── calendar_service/       #   Polish business day calendar (holidays lib)
    └── tax_service/            #   19% flat tax calculation, deductible losses
```

## Key Domain Concepts

- **NBP exchange rate rule**: Foreign transactions must be converted to PLN at the NBP
  mid-rate from the last business day *before* the transaction date (`Exchanger.get_day_one()`).
- **FIFO method**: Stock sales are matched against purchases in first-in-first-out order
  (`PerStockProfitCalculator`).
- **Deductible losses**: Losses from previous years can offset current-year profits
  (`TaxCalculator.deductible_loss_from_previous_years()`).
- **Stock splits**: Handled by adjusting historical transaction quantities
  (`StockSplitHandler`).

## Tech Stack

- **Python 3.10+** (CI uses 3.10; type hints use `X | Y` union syntax)
- **Click** — CLI argument parsing
- **Pendulum** — date/time handling
- **Requests** — NBP API calls
- **Holidays** — Polish public holidays calendar
- **Loguru** — structured logging
- **Pandas / Openpyxl** — broker data import parsing

## Environment

- `PYTHONPATH=./src` is required for all commands (set in `.env`)
- No virtualenv is committed; create one locally and `pip install -r requirements.txt`

## Testing

- Tests use `unittest.TestCase` (not pytest fixtures)
- Test helpers live in `tests/utils.py` — provides factory functions like `buy()`, `sell()`,
  `apple()`, `usd()`, `zl()` and a `StubExchanger` (uses fixed 4.0 USD→PLN rate)
- CI runs: `PYTHONPATH=./src python -m unittest discover tests`
- Flake8 linting in CI (syntax errors and undefined names only)

## Conventions

- Broker plugins go in `src/plugins/{stock,crypto}/<broker_name>/`
- Each plugin has a `__main__.py` entry point and parser modules
- Standardized CSV format is defined by `example_format.csv` in each data source directory
- Domain types use value objects (`FiatValue`, `AssetValue`) with operator overloading
- Currency enum: `Currency.DOLLAR` ("USD"), `Currency.EURO` ("EUR"), `Currency.ZLOTY` ("PLN")
