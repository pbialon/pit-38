# PIT-38 — Kalkulator podatku od inwestycji

> **[&#127468;&#127463; English version](README.md)**

Narzędzie wiersza poleceń do obliczania polskiego podatku dochodowego od **akcji** i **kryptowalut** (formularz PIT-38). Importuje historię transakcji z popularnych brokerów, przelicza waluty obce na PLN po kursach średnich NBP i oblicza wysokość podatku.

## Obsługiwani brokerzy

| Broker   | Akcje  | Krypto |
|----------|--------|--------|
| Revolut  | Tak    | Tak    |
| E*Trade  | Tak    | —      |
| Binance  | —      | Tak    |
| Ręczny CSV | Tak  | Tak    |

## Szybki start

### Instalacja

```bash
pipx install pit-38
```

Lub ze źródeł:

```bash
pipx install .
```

### Obliczanie podatku od akcji

```bash
pit38 stock -f transakcje.csv -y 2025
```

### Obliczanie podatku od kryptowalut

```bash
pit38 crypto -f transakcje.csv -y 2025
```

### Import z brokera

Konwertuj eksport brokera do ustandaryzowanego formatu CSV:

```bash
pit38 import revolut-stock  -i eksport_revolut.csv -o transakcje.csv
pit38 import revolut-crypto -i eksport_revolut.csv -o transakcje.csv
pit38 import etrade         -i eksport_etrade.csv  -o transakcje.csv
pit38 import binance        -i eksport_binance.csv -o transakcje.csv
```

Możesz łączyć pliki z różnych brokerów:

```bash
pit38 stock -f revolut.csv -f etrade.csv -y 2025
```

### Ręczny format CSV

Możesz też przygotować pliki transakcji ręcznie. Przykładowe formaty:

- Akcje: [`pit38/data_sources/stock_loader/example_format.csv`](pit38/data_sources/stock_loader/example_format.csv)
- Krypto: [`pit38/data_sources/crypto_loader/example_format.csv`](pit38/data_sources/crypto_loader/example_format.csv)

## Jak to działa

1. **Import** — pluginy brokerów konwertują eksporty CSV do ustandaryzowanego formatu
2. **Przewalutowanie** — kwoty w walutach obcych przeliczane są na PLN po kursie średnim NBP (tabela A) z ostatniego dnia roboczego przed datą transakcji
3. **Kalkulacja** — zyski z akcji obliczane metodą FIFO; kryptowaluty wg rocznej sumy kosztów i przychodów
4. **Podatek** — stawka 19% z automatycznym odliczeniem strat z lat poprzednich

## Rozwój projektu

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## Zastrzeżenie

To narzędzie służy wyłącznie **celom informacyjnym** i nie stanowi porady podatkowej. Przed złożeniem deklaracji PIT-38 zweryfikuj obliczenia z doradcą podatkowym.

---

<a href="https://www.buymeacoffee.com/pbialon" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
