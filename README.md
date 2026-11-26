# PIT-38 — Polish Investment Tax Calculator

[![CI](https://github.com/pbialon/pit-38/actions/workflows/python-app.yml/badge.svg)](https://github.com/pbialon/pit-38/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/pbialon/pit-38/graph/badge.svg)](https://codecov.io/gh/pbialon/pit-38)
[![GitHub release](https://img.shields.io/github/v/release/pbialon/pit-38)](https://github.com/pbialon/pit-38/releases)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **[&#127477;&#127473; Wersja polska](README.pl.md)**

A command-line tool for calculating Polish income tax on **stocks** and **cryptocurrency** (PIT-38 form). It imports transaction history from popular brokers, converts foreign currencies to PLN using official NBP exchange rates, and computes your tax liability.

## Supported Brokers

| Broker       | Stocks          | Crypto |
|--------------|-----------------|--------|
| Revolut      | Yes             | Yes    |
| E*Trade      | Yes             | —      |
| IBI Capital  | Yes (SELL-side, PDF input) | — |
| Binance      | —               | Yes    |
| Manual CSV   | Yes             | Yes    |

For broker-specific quirks see [`docs/BROKERS.md`](docs/BROKERS.md).

## Quick Start

### Install

```bash
pipx install pit-38
```

Or from source:

```bash
pipx install .
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
pit38 import ibi-capital    -i ~/ibi_orders/      -o transactions.csv   # PDF input (single file or directory)
```

You can combine multiple files from different brokers:

```bash
pit38 stock -f revolut.csv -f etrade.csv -y 2025
```

### Manual CSV format

You can also prepare transaction files manually. See the example formats:

- Stocks: [`pit38/data_sources/stock_loader/example_format.csv`](pit38/data_sources/stock_loader/example_format.csv)
- Crypto: [`pit38/data_sources/crypto_loader/example_format.csv`](pit38/data_sources/crypto_loader/example_format.csv)

## Document import and readiness API

Import the public data types from `pit38.api`. Schema version 1 defines the
payloads exchanged with a caller. These types describe the contract for future
importers and calculators. Existing CLI commands use their current interfaces.

- `InputDocument(document_id, content, tax_year, account_alias, declared_scope=None)`
  accepts raw `bytes`. Use local identifiers for the document and account. The
  optional scope records the caller's declaration. Keep the input on the caller
  side and use the result payloads for JSON.
- `ImportResult` identifies the document and detected variant (`None` if
  undetermined) and carries date ranges, row decisions and issues. Date ranges
  use ISO dates and mark their origin as `document`, `observed_rows` or
  `caller`. Dates observed in rows alone cannot establish full coverage.
  Producers supply one decision per data row using one-based source row
  numbers. Decisions have a classification and reason code, and can share a
  local `event_id` when rows belong to the same event.
- `Issue` includes a stable machine-readable `code`, `severity` (`error` or
  `warning`), optional source and related source references, and an optional
  `next` action identifier. Localize the display text in the caller. For
  example, `MISSING_BUY` identifies a missing purchase and
  `add_earlier_statement` requests an earlier statement. Treat codes as
  extensible.
- `ReadinessResult` carries the tax year, status, issues and form fields. A
  `blocked` result always serializes with `"form_fields": []`. A `ready`
  result requires form fields and allows warnings. The core producer is
  responsible for confirming scope and mapping before constructing a ready
  result. Form mapping and readiness evaluation are outside this schema change.

Call `to_dict()` on either result to obtain a JSON-compatible dictionary.
Collections serialize as arrays and missing optional values as `null`.
A form field's `amount` takes a finite `Decimal` and serializes as decimal
text, preserving fractional digits without exponent notation or rounding
(for example, `Decimal("620.00")` becomes `"620.00"`).

Synthetic blocked-result example:

```python
import json

from pit38.api import Issue, ReadinessResult, SourceRef

result = ReadinessResult(
    tax_year=2026,
    status="blocked",
    issues=(
        Issue(
            code="MISSING_BUY",
            severity="error",
            source=SourceRef(document="A", row=8),
            next="add_earlier_statement",
        ),
    ),
)

print(json.dumps(result.to_dict(), indent=2))
```

## Tax Rules

This calculator implements Polish tax law for capital gains (PIT-38).
For a detailed description of the rules, see:

- [Tax Rules (English)](docs/TAX_RULES.md)
- [Zasady podatkowe (Polski)](docs/TAX_RULES.pl.md)

## How It Works

1. **Import** — broker plugins convert proprietary CSV exports into a standardized format
2. **Exchange** — foreign currency amounts are converted to PLN using NBP average rates (table A) from the last business day before each transaction
3. **Calculate** — stock profits use the FIFO method; crypto uses yearly cost/income aggregation
4. **Tax** — 19% flat tax rate is applied, with automatic deduction of losses from previous years

## Contributing

Contributions are welcome — including first-time open-source PRs and new broker plugins. See **[CONTRIBUTING.md](CONTRIBUTING.md)** for dev setup, test conventions, PR guidelines, and a walkthrough for adding a new broker plugin.

Quick dev setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).

## Disclaimer

This tool is provided for **informational purposes only** and does not constitute tax advice. Always verify your calculations with a qualified tax advisor before filing your PIT-38 declaration.

## Community

- **[GitHub Discussions](https://github.com/pbialon/pit-38/discussions)** — tax-rule Q&A, broker requests, feedback. English and Polish both welcome.
- **[Issue tracker](https://github.com/pbialon/pit-38/issues)** — bug reports and feature requests.

---

<a href="https://www.buymeacoffee.com/pbialon" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
