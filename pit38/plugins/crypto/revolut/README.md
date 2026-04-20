# Revolut Crypto Plugin

## README in English

Plugin for processing cryptocurrency transaction data from Revolut.

## Usage

The plugin can be run from the command line using the following command:

```bash
python -m plugins.crypto.revolut --input-path INPUT_FILE_PATH --output-path OUTPUT_FILE_PATH
```

### Parameters

- `--input-path` (required): Path to the input CSV file with Revolut data
- `--output-path` (required): Path to the output file where processed data will be saved
- `--log-level` (optional): Logging level (default: INFO). Available options:
  - DEBUG
  - INFO
  - WARNING
  - ERROR
  - CRITICAL

### Example

```bash
python -m plugins.crypto.revolut --input-path ./revolut_data.csv --output-path ./processed_data.csv --log-level DEBUG
```

---

## README po polsku

Plugin służący do przetwarzania danych transakcji kryptowalutowych z Revolut.

## Użycie

Plugin można uruchomić z linii poleceń używając następującej komendy:

```bash
python -m plugins.crypto.revolut --input-path SCIEZKA_DO_PLIKU_WEJSCIOWEGO --output-path SCIEZKA_DO_PLIKU_WYJSCIOWEGO
```

### Parametry

- `--input-path` (wymagany): Ścieżka do pliku wejściowego CSV z danymi z Revolut
- `--output-path` (wymagany): Ścieżka do pliku wyjściowego, gdzie zostaną zapisane przetworzone dane
- `--log-level` (opcjonalny): Poziom logowania (domyślnie: INFO). Dostępne opcje:
  - DEBUG
  - INFO
  - WARNING
  - ERROR
  - CRITICAL

### Przykład użycia

```bash
python -m plugins.crypto.revolut --input-path ./dane_revolut.csv --output-path ./przetworzone_dane.csv --log-level DEBUG
```
