# E*TRADE Stock Plugin

## English

Plugin for importing stock transactions from E*TRADE.

### CSV File Format

The CSV file should contain the following columns:
- Record Type - record type (Summary or Transaction)
- Date Acquired - purchase date
- Date Sold - sale date
- Symbol - stock symbol
- Qty. - quantity of shares
- Acquisition Cost - purchase cost (in $XXX.XX format)
- Total Proceeds - sale proceeds (in $XXX.XX format)

### Usage

```bash
python -m plugins.stock.etrade --input-path INPUT_FILE_PATH --output-path OUTPUT_FILE_PATH
```

---

## Polski

Plugin do importowania transakcji giełdowych z E*TRADE.

### Format pliku CSV

Plik CSV powinien zawierać następujące kolumny:

- Record Type - typ rekordu (Summary lub Transaction)
- Date Acquired - data zakupu
- Date Sold - data sprzedaży
- Symbol - symbol akcji
- Qty. - ilość akcji
- Acquisition Cost - koszt zakupu (w formacie $XXX.XX)
- Total Proceeds - przychód ze sprzedaży (w formacie $XXX.XX)

### Użycie

```bash
python -m plugins.stock.etrade --input-path SCIEZKA_DO_PLIKU_WEJSCIOWEGO --output-path SCIEZKA_DO_PLIKU_WYJSCIOWEGO
```
