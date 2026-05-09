# Tworzenie pluginow brokerskich

Ten dokument jest dla osob, ktore chca dodac nowy import brokera do `pit-38`.

Powiazane dokumenty:
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) - setup i zasady PR
- [`docs/BROKERS.md`](BROKERS.md) - notatki per broker
- [`docs/DEVELOPING_PLUGINS.md`](DEVELOPING_PLUGINS.md) - wersja English

## 1. Czym jest plugin brokera?

Plugin brokera konwertuje eksport brokera (CSV, PDF itp.) do kanonicznego
formatu transakcji pit-38:

- `date`
- `operation`
- `amount`
- `symbol`
- `fiat_value`
- `currency`

Po konwersji standardowe loadery i kalkulatory podatku robia reszte.

## 2. Kontrakt pluginu (aktualny kod)

W repo nie ma teraz jednej klasy `BrokerPlugin`. Kontrakt jest podzielony:

1. Komenda CLI importu w [`pit38/cli.py`](../pit38/cli.py)
2. Parser/czytnik mapujacy wiersze brokera na obiekty domenowe
3. Saver zapisujacy kanoniczny CSV

Dla pluginow stock formatowanie opiera sie o `BaseFormatter`:

```python
class BaseFormatter(ABC):
    @abstractmethod
    def format(self, item: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def item_type(self) -> Type:
        pass
```

Pliki referencyjne:
- [`pit38/plugins/stock/formatters.py`](../pit38/plugins/stock/formatters.py)
- [`pit38/plugins/stock/generic_saver.py`](../pit38/plugins/stock/generic_saver.py)
- [`pit38/plugins/crypto/generic_saver.py`](../pit38/plugins/crypto/generic_saver.py)

## 3. Krok po kroku: nowy broker (cookiecutter)

### 3.1 Scaffold

```bash
pip install cookiecutter
cookiecutter gh:pbialon/pit-38-broker-template
```

### 3.2 Sprawdz wygenerowane pliki

Minimum:
- modul parsera
- modul csv reader/service
- punkt wejscia CLI
- testy parsera/service
- README pluginu

### 3.3 Zdobadz realny eksport

Uzyj prawdziwego eksportu brokera, ale zanonimizuj dane:
- usun id kont
- usun imiona/nazwiska
- zostaw oryginalny format liczb i dat

### 3.4 Napisz parser

Mapuj typy operacji brokera na domenowe:
- `BUY`
- `SELL`
- `DIVIDEND`
- `SERVICE_FEE`
- `STOCK_SPLIT` (tylko stock)

Wynik pluginu ma byc tylko w kanonicznych kolumnach CSV.

### 3.5 Podepnij komende do CLI

Zarejestruj pod `pit38 import` w [`pit38/cli.py`](../pit38/cli.py):
- opcja input path
- opcja output path
- opcjonalnie `--log-level`
- krotkie podsumowanie po imporcie

### 3.6 Uruchom testy

```bash
pytest tests/
pytest tests/ --cov=pit38 --cov-branch
```

### 3.7 Otworz PR

- podlacz issue (`Closes #...`)
- dodaj wpis do changelog
- opisz impact podatkowy w template PR

## 4. Typowe wzorce

### Parsowanie dat

- `pendulum.parse(...)` dla formatow ISO-like
- `datetime.strptime(...)` dla niestandardowych formatow

Przyklad: Binance parser uzywa `%y-%m-%d %H:%M:%S` w
[`pit38/plugins/crypto/binance/csv.py`](../pit38/plugins/crypto/binance/csv.py).

### Normalizacja walut i kwot

Uzywaj wspolnych helperow zamiast nowego regexa per plugin:
- `normalize_currency_layout`
- `parse_amount`

z [`pit38/plugins/normalization.py`](../pit38/plugins/normalization.py).

### Brakujace kolumny i uszkodzone wiersze

- fail fast przy brakujacych wymaganych kolumnach
- nieznane nietaxowe operacje pomijaj z czytelnym warningiem
- nie wywalaj calego importu przez jeden zly wiersz, jesli flow ma byc tolerancyjny

### Znaki kwot i fee

Jawnie trzymaj semantyke:
- service fee to koszt
- dividend to przychod
- nie odwroc znaku "po cichu" bez testu, ktory to dokumentuje

## 5. Testowanie pluginu

Helpery z [`tests/utils.py`](../tests/utils.py):
- `buy()`, `sell()`, `apple()`, `usd()`, `zl()`
- `StubExchanger`

Warstwy testow:
- unit test parsera (row -> obiekt domenowy)
- test csv service (plik -> lista obiektow)
- e2e z fixture po anonimizacji w `tests/e2e/fixtures/`

Minimalny szkic testu parsera:

```python
from unittest import TestCase
from tests.utils import buy, apple, usd

class TestMyBrokerParser(TestCase):
    def test_buy_row(self):
        row = {"date": "2025-01-02 10:00:00", "type": "BUY", "qty": "1", "ticker": "AAPL", "value": "USD 200.00"}
        tx = parse_row(row)
        self.assertEqual(tx, buy(apple(1), usd(200.0), "2025-01-02 10:00:00"))
```

## 6. Checklista poprawnosci podatkowej

Przed PR sprawdz:

- Traktowanie fee:
  - fee jest juz w kwocie gross?
  - fee idzie osobna operacja?
- Gross vs net:
  - przychod jest net czy gross?
  - czy fee nie jest policzone podwojnie?
- Potracenie podatku od dywidendy:
  - broker daje gross, net czy oba?
  - ktora kwota jest kanoniczna dla PIT-38?
- Waluta:
  - oryginalna waluta jest zachowana przed konwersja NBP?
- Stock split:
  - ratio zapisane bez sztucznego fiat value?

Przy watpliwosciach wrzuc sample (zanonimizowany) do Discussions.

## 7. Przyklady (od scaffold do gotowego pluginu)

### 7.1 Revolut stock

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

Pliki:
- [`pit38/plugins/stock/revolut/transaction_row_parser.py`](../pit38/plugins/stock/revolut/transaction_row_parser.py)
- [`pit38/plugins/stock/revolut/operation_row_parser.py`](../pit38/plugins/stock/revolut/operation_row_parser.py)

### 7.2 Binance crypto

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

Plik:
- [`pit38/plugins/crypto/binance/csv.py`](../pit38/plugins/crypto/binance/csv.py)

## 8. Przeplyw transakcji

```mermaid
graph LR
    A[Broker CSV] --> B[RowParser]
    B --> C[Canonical CSV]
    C --> D[GenericCsvLoader]
    D --> E[Transaction objects]
    E --> F[Tax Calculator]
```

## 9. Gdzie pytac

- Discussions: <https://github.com/pbialon/pit-38/discussions>
- Issues: <https://github.com/pbialon/pit-38/issues>
- Zasady podatkowe:
  - [`docs/TAX_RULES.md`](TAX_RULES.md)
  - [`docs/TAX_RULES.pl.md`](TAX_RULES.pl.md)
