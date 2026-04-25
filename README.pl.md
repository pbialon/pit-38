# PIT-38 — Kalkulator podatku od inwestycji

[![CI](https://github.com/pbialon/pit-38/actions/workflows/python-app.yml/badge.svg)](https://github.com/pbialon/pit-38/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/pbialon/pit-38/graph/badge.svg)](https://codecov.io/gh/pbialon/pit-38)
[![GitHub release](https://img.shields.io/github/v/release/pbialon/pit-38)](https://github.com/pbialon/pit-38/releases)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **[&#127468;&#127463; English version](README.md)**

Narzędzie wiersza poleceń do obliczania polskiego podatku dochodowego od **akcji** i **kryptowalut** (formularz PIT-38). Importuje historię transakcji z popularnych brokerów, przelicza waluty obce na PLN po kursach średnich NBP i oblicza wysokość podatku.

## Obsługiwani brokerzy

| Broker       | Akcje                         | Krypto |
|--------------|-------------------------------|--------|
| Revolut      | Tak                           | Tak    |
| E*Trade      | Tak                           | —      |
| IBI Capital  | Tak (tylko sprzedaże, input PDF) | —   |
| Binance      | —                             | Tak    |
| Ręczny CSV   | Tak                           | Tak    |

Specyfika poszczególnych brokerów — zob. [`docs/BROKERS.md`](docs/BROKERS.md).

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
pit38 import ibi-capital    -i ~/ibi_orders/       -o transakcje.csv   # input: PDF; instalacja: pipx install 'pit-38[ibi]'
```

Możesz łączyć pliki z różnych brokerów:

```bash
pit38 stock -f revolut.csv -f etrade.csv -y 2025
```

### Ręczny format CSV

Możesz też przygotować pliki transakcji ręcznie. Przykładowe formaty:

- Akcje: [`pit38/data_sources/stock_loader/example_format.csv`](pit38/data_sources/stock_loader/example_format.csv)
- Krypto: [`pit38/data_sources/crypto_loader/example_format.csv`](pit38/data_sources/crypto_loader/example_format.csv)

## Zasady podatkowe

Kalkulator implementuje polskie prawo podatkowe dot. zysków kapitałowych (PIT-38).
Szczegółowy opis zasad:

- [Tax Rules (English)](docs/TAX_RULES.md)
- [Zasady podatkowe (Polski)](docs/TAX_RULES.pl.md)

## Jak to działa

1. **Import** — pluginy brokerów konwertują eksporty CSV do ustandaryzowanego formatu
2. **Przewalutowanie** — kwoty w walutach obcych przeliczane są na PLN po kursie średnim NBP (tabela A) z ostatniego dnia roboczego przed datą transakcji
3. **Kalkulacja** — zyski z akcji obliczane metodą FIFO; kryptowaluty wg rocznej sumy kosztów i przychodów
4. **Podatek** — stawka 19% z automatycznym odliczeniem strat z lat poprzednich

## Współtworzenie

Zapraszamy do kontrybucji — również osoby, dla których to pierwsza przygoda z open source, oraz chętnych do dodania wsparcia nowego brokera. Pełny przewodnik znajdziesz w **[CONTRIBUTING.md](CONTRIBUTING.md)** (konfiguracja środowiska, testy, wytyczne do PR i instrukcja dodawania pluginu brokera). Issues i PR-y po polsku są mile widziane.

Szybka konfiguracja środowiska:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

Projekt przestrzega [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).

## Zastrzeżenie

To narzędzie służy wyłącznie **celom informacyjnym** i nie stanowi porady podatkowej. Przed złożeniem deklaracji PIT-38 zweryfikuj obliczenia z doradcą podatkowym.

## Społeczność

- **[GitHub Discussions](https://github.com/pbialon/pit-38/discussions)** — pytania o zasady podatkowe, prośby o wsparcie nowych brokerów, feedback. Po polsku i angielsku.
- **[Issue tracker](https://github.com/pbialon/pit-38/issues)** — zgłoszenia błędów i propozycje funkcji.

---

<a href="https://www.buymeacoffee.com/pbialon" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
