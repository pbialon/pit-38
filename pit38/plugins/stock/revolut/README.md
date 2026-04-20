# Revolut Stock Plugin

## English

Plugin for importing stock transactions from Revolut, including BUY/SELL trades, dividends, custody fees, and stock splits.

### Usage

```bash
python -m pit38.plugins.stock.revolut --input-path INPUT_FILE --output-path OUTPUT_FILE
```

### Parameters

- `--input-path` (required): Path to Revolut stock export CSV
- `--output-path` (required): Path for the standardized output CSV
- `--log-level` (optional): DEBUG, INFO (default), WARNING, ERROR, CRITICAL

### Note on stock splits

When a stock split is detected, the plugin will interactively ask for the split ratio (e.g., `20` for a 20:1 split).

---

## Polski

Plugin do importu transakcji giełdowych z Revolut — obsługuje transakcje BUY/SELL, dywidendy, opłaty za przechowywanie i splity akcji.

### Użycie

```bash
python -m pit38.plugins.stock.revolut --input-path PLIK_WEJSCIOWY --output-path PLIK_WYJSCIOWY
```

### Parametry

- `--input-path` (wymagany): Ścieżka do eksportu CSV z Revolut
- `--output-path` (wymagany): Ścieżka do ustandaryzowanego pliku wyjściowego
- `--log-level` (opcjonalny): DEBUG, INFO (domyślnie), WARNING, ERROR, CRITICAL

### Uwaga dotycząca splitów akcji

Gdy wykryty zostanie split akcji, plugin interaktywnie zapyta o współczynnik podziału (np. `20` dla splitu 20:1).
