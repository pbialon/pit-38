# Developing Broker Plugins

This guide is for contributors who want to add support for a new broker import
in `pit-38`.

Related docs:
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) for setup and PR rules
- [`docs/BROKERS.md`](BROKERS.md) for broker-specific notes
- [`docs/DEVELOPING_PLUGINS.pl.md`](DEVELOPING_PLUGINS.pl.md) for Polish version

## 1. What is a broker plugin?

A broker plugin converts a broker export (CSV, PDF, etc.) into pit-38's
canonical transaction shape:

- `date`
- `operation`
- `amount`
- `symbol`
- `fiat_value`
- `currency`

After conversion, normal loaders and tax calculators process the output.

## 2. Broker plugin contract (current code)

There is no single `BrokerPlugin` class in the repo right now. The contract is
split into small pieces:

1. A CLI import command in [`pit38/cli.py`](../pit38/cli.py)
2. A parser/reader that maps broker rows to domain objects
3. A saver that writes canonical CSV

For stock plugins, formatting is driven by `BaseFormatter`:

```python
class BaseFormatter(ABC):
    @abstractmethod
    def format(self, item: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def item_type(self) -> Type:
        pass
```

Reference files:
- [`pit38/plugins/stock/formatters.py`](../pit38/plugins/stock/formatters.py)
- [`pit38/plugins/stock/generic_saver.py`](../pit38/plugins/stock/generic_saver.py)
- [`pit38/plugins/crypto/generic_saver.py`](../pit38/plugins/crypto/generic_saver.py)

## 3. Step by step: add a new broker (cookiecutter flow)

### 3.1 Scaffold

```bash
pip install cookiecutter
cookiecutter gh:pbialon/pit-38-broker-template
```

### 3.2 Inspect generated files

At minimum, confirm:
- parser module
- csv reader/service module
- CLI entry module or function
- tests for parser/service
- README for the plugin

### 3.3 Get a real export sample

Use real broker exports with sanitized personal data:
- remove account ids
- remove names
- keep numeric and date format exactly as in source

### 3.4 Implement parsing

Map broker-specific operation names to domain operations:
- `BUY`
- `SELL`
- `DIVIDEND`
- `SERVICE_FEE`
- `STOCK_SPLIT` (stocks only)

Write plugin output in canonical columns only.

### 3.5 Wire into CLI

Register command under `pit38 import` in [`pit38/cli.py`](../pit38/cli.py):
- input path option(s)
- output path option
- optional `--log-level`
- short success summary

### 3.6 Run tests

```bash
pytest tests/
pytest tests/ --cov=pit38 --cov-branch
```

### 3.7 Open PR

- link issue (`Closes #...`)
- include changelog line
- mention tax impact in PR template

## 4. Common patterns

### Date parsing

- Prefer `pendulum.parse(...)` when source is ISO-like
- Use explicit `datetime.strptime(...)` for custom formats

Example: Binance parser uses `%y-%m-%d %H:%M:%S` in
[`pit38/plugins/crypto/binance/csv.py`](../pit38/plugins/crypto/binance/csv.py).

### Currency and amount normalization

Use shared helpers instead of new regex per plugin:
- `normalize_currency_layout`
- `parse_amount`

From [`pit38/plugins/normalization.py`](../pit38/plugins/normalization.py).

### Missing columns and malformed rows

- Fail early on missing required columns
- Skip unknown non-tax-relevant rows with clear warning
- Do not crash whole import on one bad row if behavior should be tolerant

### Signed amounts and fee handling

Keep semantics explicit:
- service fee is cost
- dividend is income
- do not silently flip signs without a test that documents why

## 5. Testing your plugin

Use helpers from [`tests/utils.py`](../tests/utils.py):
- `buy()`, `sell()`, `apple()`, `usd()`, `zl()`
- `StubExchanger`

Typical test layers:
- parser unit tests (row -> domain object)
- csv service tests (file -> list of objects)
- e2e test with sanitized fixture in `tests/e2e/fixtures/`

Minimal parser test sketch:

```python
from unittest import TestCase
from tests.utils import buy, apple, usd

class TestMyBrokerParser(TestCase):
    def test_buy_row(self):
        row = {"date": "2025-01-02 10:00:00", "type": "BUY", "qty": "1", "ticker": "AAPL", "value": "USD 200.00"}
        tx = parse_row(row)
        self.assertEqual(tx, buy(apple(1), usd(200.0), "2025-01-02 10:00:00"))
```

## 6. Tax-correctness checklist

Before opening PR, verify:

- Fee treatment:
  - broker fee included in gross row?
  - broker fee emitted as separate operation?
- Gross vs net:
  - are proceeds net of fee or gross?
  - did you avoid double-counting fee?
- Dividend withholding:
  - broker reports gross dividend, net dividend, or both?
  - which amount is canonical for PIT-38 flow here?
- Currency:
  - original currency preserved before NBP conversion?
- Stock split:
  - ratio stored without fake fiat value?

If in doubt, open a Discussion with anonymized sample rows.

## 7. Worked examples (before scaffold -> after plugin)

### 7.1 Revolut stock example

```diff
# scaffold (generated)
class RowParser:
    def parse(self, row):
        raise NotImplementedError

# after implementation
class TransactionRowParser(RowParser):
    OPERATIONS_HANDLED = {OperationType.BUY, OperationType.SELL}

    @classmethod
    def parse(cls, row):
        operation_type = cls._operation_type(row)
        if operation_type not in cls.OPERATIONS_HANDLED:
            return None
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._fiat_value(row),
            action=operation_type,
            date=cls._date(row),
        )
```

Related files:
- [`pit38/plugins/stock/revolut/transaction_row_parser.py`](../pit38/plugins/stock/revolut/transaction_row_parser.py)
- [`pit38/plugins/stock/revolut/operation_row_parser.py`](../pit38/plugins/stock/revolut/operation_row_parser.py)

### 7.2 Binance crypto example

```diff
# scaffold (generated)
def read(path):
    return []

# after implementation
class BinanceTransactionProcessor:
    def read(self, file_path: str) -> List[Transaction]:
        convert_operations = []
        transaction_operations = []
        with open_csv_reader(file_path) as reader:
            for row in reader:
                tx = BinanceTransaction(row)
                if tx.operation_type() == BinanceOperationType.DEPOSIT:
                    continue
                if tx.operation_type() == BinanceOperationType.CONVERT:
                    convert_operations.append(tx)
                else:
                    transaction_operations.append(tx)
        all_transactions = (
            self._process_convert_transactions(convert_operations)
            + self._process_transaction_operations(transaction_operations)
        )
        return sorted(all_transactions, key=lambda x: x.date)
```

Related file:
- [`pit38/plugins/crypto/binance/csv.py`](../pit38/plugins/crypto/binance/csv.py)

## 8. Transaction flow

```mermaid
graph LR
    A[Broker CSV] --> B[RowParser]
    B --> C[Canonical CSV]
    C --> D[GenericCsvLoader]
    D --> E[Transaction objects]
    E --> F[Tax Calculator]
```

## 9. Getting help

- Discussions: <https://github.com/pbialon/pit-38/discussions>
- Issues: <https://github.com/pbialon/pit-38/issues>
- Tax rules docs:
  - [`docs/TAX_RULES.md`](TAX_RULES.md)
  - [`docs/TAX_RULES.pl.md`](TAX_RULES.pl.md)
