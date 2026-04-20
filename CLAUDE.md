# PIT-38 — Polish Investment Tax Calculator

## Project Overview

CLI tool for calculating Polish income tax on stocks and cryptocurrency (PIT-38 form).
Supports importing transaction data from multiple brokers (Revolut, E*Trade, Binance),
converting foreign currencies to PLN using NBP (National Bank of Poland) exchange rates,
and computing tax liability at the 19% flat rate.

## Quick Reference

```bash
# Install (user)
pipx install .

# Install (development)
pip install -e ".[dev]"

# Run stock tax calculation
pit38 stock -f <file1> -f <file2> -y 2025

# Run crypto tax calculation
pit38 crypto -f <file1> -y 2025

# Import from broker (Revolut stocks example)
python -m pit38.plugins.stock.revolut --input-path <export> --output-path <output>

# Run tests
pytest tests/
```

## Architecture

```
pit38/                          # Main Python package
├── cli.py                      # Unified CLI entry point (click.group)
├── stock.py / crypto.py        # Subcommands (Click commands)
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

- **Python 3.10+** (type hints use `X | Y` union syntax)
- **Click** — CLI argument parsing
- **Pendulum** — date/time handling
- **Requests** — NBP API calls
- **Holidays** — Polish public holidays calendar
- **Loguru** — structured logging
- **Pandas / Openpyxl** — broker data import parsing

## Packaging

- `pyproject.toml` defines the package, dependencies, and CLI entry point (`pit38`)
- Install with `pipx install .` (user) or `pip install -e ".[dev]"` (development)
- No `PYTHONPATH` hacks needed — proper Python package with `pit38.*` imports
- **Versioning:** CalVer `YYYY.M.DD` (e.g., `2026.4.20`). Set the version in `pyproject.toml`
  to the release date. Calendar versioning fits a tax tool — it's immediately clear whether
  a release covers the current tax year's rules.

## Testing

- Tests use `unittest.TestCase` (not pytest fixtures)
- Test helpers live in `tests/utils.py` — provides factory functions like `buy()`, `sell()`,
  `apple()`, `usd()`, `zl()` and a `StubExchanger` (uses fixed 4.0 USD→PLN rate)
- CI: `pip install -e ".[dev]"` then `pytest tests/`
- Flake8 linting in CI (syntax errors and undefined names only)

## Conventions

- Broker plugins go in `pit38/plugins/{stock,crypto}/<broker_name>/`
- Each plugin has a `__main__.py` entry point and parser modules
- Standardized CSV format is defined by `example_format.csv` in each data source directory
- Domain types use value objects (`FiatValue`, `AssetValue`) with operator overloading
- Currency enum: `Currency.DOLLAR` ("USD"), `Currency.EURO` ("EUR"), `Currency.ZLOTY` ("PLN")
- All imports use the `pit38.` package prefix (e.g., `from pit38.domain.xxx import Yyy`)
