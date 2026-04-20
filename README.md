# PIT-38 — Polish Investment Tax Calculator

> **[&#127477;&#127473; Wersja polska](README.pl.md)**

A command-line tool for calculating Polish income tax on **stocks** and **cryptocurrency** (PIT-38 form). It imports transaction history from popular brokers, converts foreign currencies to PLN using official NBP exchange rates, and computes your tax liability.

## Supported Brokers

| Broker   | Stocks | Crypto |
|----------|--------|--------|
| Revolut  | Yes    | Yes    |
| E*Trade  | Yes    | —      |
| Binance  | —      | Yes    |
| Manual CSV | Yes  | Yes    |

## Quick Start

### Install

```bash
pipx install .
```

Or with pip in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### Calculate stock tax

```bash
pit38 stock -f transactions.csv -y 2025
```

### Calculate crypto tax

```bash
pit38 crypto -f transactions.csv -y 2025
```

### Import from broker

Convert your broker's export into the standardized CSV format:

```bash
pit38 import revolut-stock  -i revolut_export.csv -o transactions.csv
pit38 import revolut-crypto -i revolut_export.csv -o transactions.csv
pit38 import etrade         -i etrade_export.csv  -o transactions.csv
pit38 import binance        -i binance_export.csv -o transactions.csv
```

You can combine multiple files from different brokers:

```bash
pit38 stock -f revolut.csv -f etrade.csv -y 2025
```

### Manual CSV format

You can also prepare transaction files manually. See the example formats:

- Stocks: [`pit38/data_sources/stock_loader/example_format.csv`](pit38/data_sources/stock_loader/example_format.csv)
- Crypto: [`pit38/data_sources/crypto_loader/example_format.csv`](pit38/data_sources/crypto_loader/example_format.csv)

## How It Works

1. **Import** — broker plugins convert proprietary CSV exports into a standardized format
2. **Exchange** — foreign currency amounts are converted to PLN using NBP average rates (table A) from the last business day before each transaction
3. **Calculate** — stock profits use the FIFO method; crypto uses yearly cost/income aggregation
4. **Tax** — 19% flat tax rate is applied, with automatic deduction of losses from previous years

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## Disclaimer

This tool is provided for **informational purposes only** and does not constitute tax advice. Always verify your calculations with a qualified tax advisor before filing your PIT-38 declaration.

---

<a href="https://www.buymeacoffee.com/pbialon" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
