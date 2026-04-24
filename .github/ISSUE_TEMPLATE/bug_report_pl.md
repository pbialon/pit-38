---
name: "\U0001F1F5\U0001F1F1 Zgłoszenie błędu"
about: Zgłoś nieprawidłowe obliczenia podatku lub awarię narzędzia
title: "[BŁĄD] "
labels: ["bug"]
---

<!-- Dzięki za zgłoszenie błędu! Wypełnij poniższe sekcje — niekompletne
     zgłoszenia są trudniejsze do naprawy. Pytania o interpretację przepisów
     podatkowych (nie błędy w kodzie) zgłaszaj w Discussions → Q&A. -->

## Środowisko

- **Wersja pit-38** (uruchom `pip show pit-38 | grep Version`):
- **Wersja Pythona**:
- **System operacyjny**:
- **Broker(zy)**:
- **Rok podatkowy**:

## Co się stało

<!-- Opisz problem w 1-3 zdaniach. Jeśli wynik podatku jest błędny, podaj
     oczekiwaną vs faktyczną wartość; jeśli narzędzie się wysypało, wklej
     pełny traceback. -->

## Minimalny plik CSV do odtworzenia

<!-- ⚠️ UWAGA: usuń dane osobowe przed wklejeniem.
     - Usuń numery kont, identyfikatory, inne dane osobowe
     - Zachowaj tylko 5-10 transakcji które wywołują błąd
     - NIE wklejaj pełnych eksportów z brokera -->

```csv
wklej tutaj zanonimizowany CSV
```

## Oczekiwany wynik podatku

<!-- Jakie wartości powinny pojawić się w output CLI? Jeśli oczekiwana
     wartość wynika z konkretnego przepisu, powołaj się na artykuł
     ustawy (np. "art. 22 ust. 16 mówi że carry-forward kosztów krypto
     jest bezterminowy, więc oczekuję X PLN odliczalnych strat z 2022"). -->

## Faktyczny wynik lub błąd

<!-- Wklej pełny output CLI lub Python traceback. Jeśli możliwe, uruchom
     z `--log-level DEBUG` dla większego kontekstu. -->

```
wklej output tutaj
```

## Dodatkowe informacje

<!-- Cokolwiek jeszcze? Powiązane issues, co już próbowałeś, itp. -->
