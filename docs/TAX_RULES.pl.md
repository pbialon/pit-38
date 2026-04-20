# Zasady podatkowe PIT-38 — Podatek od zysków kapitałowych

> **[🇬🇧 English version](TAX_RULES.md)**

Dokument opisuje zasady podatkowe zaimplementowane w kalkulatorze pit-38,
zgodnie z ustawą z dnia 26 lipca 1991 r. o podatku dochodowym od osób
fizycznych (Dz.U.2025.163 t.j.).

Stan prawny: kwiecień 2026 r.

---

## Spis treści

1. [Przegląd](#1-przegląd)
2. [Stawka podatkowa](#2-stawka-podatkowa)
3. [Przeliczanie walut — kurs NBP](#3-przeliczanie-walut)
4. [Metoda FIFO dla akcji](#4-metoda-fifo)
5. [Odliczanie strat — akcje](#5-odliczanie-strat--akcje)
6. [Przenoszenie kosztów — kryptowaluty](#6-przenoszenie-kosztów--kryptowaluty)
7. [Separacja źródeł — akcje vs krypto](#7-separacja-źródeł)
8. [Przepisy przejściowe](#8-przepisy-przejściowe)
9. [Dywidendy](#9-dywidendy)
10. [Źródła](#10-źródła)

---

## 1. Przegląd

PIT-38 to roczne zeznanie podatkowe od dochodów kapitałowych. Obejmuje:

- Sprzedaż **papierów wartościowych** (akcje, obligacje, ETF) — art. 30b ust. 1
- Sprzedaż **instrumentów pochodnych** (opcje, kontrakty) — art. 30b ust. 1
- Sprzedaż **udziałów (akcji)** w spółkach — art. 30b ust. 1
- Odkupienie **jednostek funduszy inwestycyjnych** (od 2024 r.) — art. 30b ust. 1 pkt 5
- Sprzedaż **walut wirtualnych** (kryptowaluty) — art. 30b ust. 1a

Termin złożenia: **30 kwietnia** roku następującego po roku podatkowym.
PIT-38 należy złożyć nawet przy stracie (aby zachować prawo do odliczenia).

---

## 2. Stawka podatkowa

**19% zryczałtowany podatek** od dochodów kapitałowych (art. 30b ust. 1, 1a).

Podatek = max(0, podstawa_opodatkowania × 0,19)

Gdzie `podstawa = przychód − koszty − straty_z_lat_ubiegłych`.

---

## 3. Przeliczanie walut

### Podstawa prawna: art. 11a ust. 1

Kwoty w walutach obcych przelicza się na PLN po **średnim kursie NBP**
(Narodowy Bank Polski, tabela „a") z **ostatniego dnia roboczego
poprzedzającego** dzień transakcji.

### Implementacja

- „Dzień roboczy" wyklucza weekendy (sobota, niedziela) oraz polskie święta
- Jeśli dzień przed transakcją nie jest dniem roboczym, cofamy się dalej
- Przykład: transakcja w poniedziałek 3 stycznia → kurs z piątku 31 grudnia
  (chyba że 31.12 to święto — wtedy 30.12 itd.)

Metodę tę implementuje `Exchanger.get_day_one()`.

---

## 4. Metoda FIFO

### Podstawa prawna: art. 30a ust. 3

Przy sprzedaży papierów wartościowych koszt uzyskania ustala się metodą
**FIFO** (First In, First Out). Najpierw sprzedawane są akcje kupione
najwcześniej.

### Implementacja

Każdy ticker ma własną kolejkę FIFO. Przy sprzedaży:
1. Dopasuj do najstarszej pozycji kupna
2. Jeśli sprzedaż wyczerpuje pozycję — przejdź do następnej
3. Przy częściowej sprzedaży — podziel pozycję proporcjonalnie
4. Koszt przeliczany na PLN po kursie z **daty kupna** (nie sprzedaży)

Implementuje to `PerStockProfitCalculator` z `Queue`.

---

## 5. Odliczanie strat — akcje

### Podstawa prawna: art. 9 ust. 3

Strata z kapitałów pieniężnych (akcje, obligacje, instrumenty pochodne, fundusze
inwestycyjne od 2024 r.) może być odliczona od dochodu z **tego samego źródła**
w **5 kolejnych latach podatkowych**, na dwa sposoby:

#### Sposób 1 — Stopniowe odliczanie (domyślny)

Odliczenie w każdym z 5 kolejnych lat, **maksymalnie 50% kwoty straty rocznie**.

Przykład: strata 10 000 PLN w 2023 r.
- 2024: odliczenie max 5 000 PLN
- 2025: odliczenie max 5 000 PLN
- ...aż do 2028 (5 lat od 2023)

#### Sposób 2 — Jednorazowe odliczenie do 5 000 000 PLN

Jednorazowe odliczenie w jednym z 5 kolejnych lat podatkowych, **do kwoty
5 000 000 PLN**. Nieodliczona reszta — w pozostałych latach tego 5-letniego
okresu, z limitem 50% straty rocznie.

Przykład: strata 8 000 000 PLN w 2023 r.
- 2024: jednorazowe odliczenie 5 000 000 PLN
- 2025–2028: reszta (3 000 000 PLN), max 50% straty/rok = max 4 000 000 PLN/rok

### Uproszczenie praktyczne

Dla strat poniesionych od 2019 r. o wartości poniżej 5 mln PLN, opcja
jednorazowa oznacza, że **całą stratę można odliczyć od razu** — limit 50%
nie ma znaczenia. Limit 50% obowiązuje tylko gdy:
- Strata powstała w 2018 r. lub wcześniej (stare zasady), LUB
- Strata przekracza 5 000 000 PLN

### Ograniczenia

- **Limit czasowy**: wyłącznie 5 kolejnych lat podatkowych po roku straty
- **Limit kwotowy**: max 50% straty rocznie (lub 5 mln PLN jednorazowo)
- **To samo źródło**: strata z kapitałów pieniężnych odliczana wyłącznie od dochodu
  z kapitałów pieniężnych (art. 30b ust. 1)
- **Obowiązek złożenia PIT-38**: nawet przy stracie — inaczej nie ma podstawy
  do odliczenia w przyszłości

---

## 6. Przenoszenie kosztów — kryptowaluty

### Podstawa prawna: art. 22 ust. 16

### Mechanizm przenoszenia kosztów (NIE strat!)

Kryptowaluty **nie podlegają** zasadom odliczania strat z art. 9 ust. 3.
Zamiast tego stosuje się odrębny mechanizm z **art. 22 ust. 16**:

> Nadwyżka kosztów uzyskania przychodów nad przychodami z odpłatnego zbycia
> waluty wirtualnej uzyskanymi w roku podatkowym **powiększa koszty uzyskania
> przychodów** z tytułu odpłatnego zbycia waluty wirtualnej poniesione
> **w następnym roku podatkowym**.

### Kluczowe różnice wobec akcji

| Cecha | Akcje (art. 9 ust. 3) | Kryptowaluty (art. 22 ust. 16) |
|-------|----------------------|-------------------------------|
| Nazwa mechanizmu | Odliczenie straty | Przeniesienie nadwyżki kosztów |
| Limit czasowy | 5 kolejnych lat | **Brak limitu** (*) |
| Limit roczny | Max 50% straty | **Brak limitu** |
| Jednorazowe odliczenie | Do 5 mln PLN | Nie dotyczy |
| Wykazywane jako | Strata w PIT-38 (sekcja C/D) | Koszty w PIT-38 (sekcja E) |

(*) Literalna treść art. 22 ust. 16 mówi o "następnym roku podatkowym" (l.poj.),
ale Dyrektor KIS w interpretacjach potwierdził, że nadwyżka kosztów może być
rozliczana w **kolejnych latach podatkowych bez ograniczenia czasowego**
(wykładnia celowościowa).

### Obowiązek składania PIT-38 bez przychodu

Zgodnie z art. 30b ust. 6a, PIT-38 należy złożyć **nawet jeśli w danym roku
nie było przychodów z krypto**, ale poniesiono koszty nabycia walut wirtualnych.
Dzięki temu koszty zostaną wykazane i przeniesione na kolejny rok.

---

## 7. Separacja źródeł

### Co z czym można łączyć

Zgodnie z **art. 30b ust. 5d**:

> Dochodów z odpłatnego zbycia walut wirtualnych **nie łączy się** z dochodami
> opodatkowanymi na zasadach określonych w ust. 1 [papiery wartościowe]
> oraz w art. 27 lub art. 30c.

Zgodnie z **art. 9 ust. 3a pkt 2** — nie można pomniejszać dochodu z walut
wirtualnych o straty z innych kapitałów pieniężnych.

### Tabela kompensacji

| Strata z → | Odliczenie od ↓ | Dozwolone? |
|------------|-----------------|------------|
| Akcje | Akcje | TAK |
| Akcje | Obligacje | TAK (*) |
| Akcje | Instrumenty pochodne | TAK (*) |
| Akcje | Fundusze inwestycyjne | TAK (od 2024) (*) |
| Akcje | Kryptowaluty | **NIE** |
| Kryptowaluty | Kryptowaluty | TAK |
| Kryptowaluty | Akcje | **NIE** |
| Kryptowaluty | Fundusze | **NIE** |

(*) Wszystkie te instrumenty należą do tego samego źródła przychodu — "kapitały
pieniężne" opodatkowane na podstawie art. 30b ust. 1. Strata z jednego typu
można odliczyć od dochodu z innego typu w ramach tego źródła.

### Zmiana od 2024 r. — fundusze inwestycyjne

Od 2024 r. dochody z funduszy inwestycyjnych (odkupienie/konwersja jednostek)
są rozliczane samodzielnie przez podatnika w PIT-38 (wcześniej pobierał podatek
fundusz). Dzięki temu:
- Straty z funduszy można kompensować z zyskami z akcji i odwrotnie
- Straty z funduszy poniesione **przed 2024** nie podlegają odliczeniu

---

## 8. Przepisy przejściowe

### Straty sprzed 2019 r.

Nowelizacja z 9 listopada 2018 r. wprowadziła opcję jednorazowego odliczenia
do 5 mln PLN (sposób 2). Nowe zasady dotyczą **strat poniesionych w latach
podatkowych rozpoczynających się po 31 grudnia 2018 r.**, czyli od roku 2019.

| Rok straty | Metody odliczenia | Okres odliczenia |
|------------|------------------|-----------------|
| ≤ 2018 | Tylko 50% rocznie (stare zasady) | 5 lat od straty |
| ≥ 2019 | 50% rocznie **lub** jednorazowo do 5 mln PLN | 5 lat od straty |

**Uwaga**: Straty z 2018 r. i wcześniejsze mogły być odliczane do 2023 r.
(5 lat). Na dzień dzisiejszy (2026 r.) najstarsza odliczalna strata pochodzi
z roku **2021** (odliczalna w latach 2022–2026).

---

## 9. Dywidendy

### Przegląd

Dywidendy z zagranicznych akcji (np. amerykańskie przez Revolut) podlegają
podatkowi u źródła na podstawie umów o unikaniu podwójnego opodatkowania.

**Akcje USA z formularzem W-8BEN**: 15% podatek pobrany w USA → 4% dopłaty
w Polsce (19% − 15%). Bez W-8BEN: 30% podatek USA → 0% w Polsce (nadwyżki
nie można odzyskać).

Kalkulator pokazuje przychody z dywidend, ale nie oblicza kompensacji
podatku u źródła. Informacja ta ma charakter poglądowy.

---

## 10. Źródła

### Ustawa

- Ustawa z dnia 26 lipca 1991 r. o podatku dochodowym od osób fizycznych
  (Dz.U.2025.163 t.j.) — art. 9 ust. 3, art. 22 ust. 16, art. 30b

### Portale podatkowe

- [Stockbroker.pl — Jak rozliczać straty z lat ubiegłych](https://stockbroker.pl/jak-rozliczac-straty-z-lat-ubieglych-2025/)
- [e-pity.pl — Podatek od kryptowalut](https://www.e-pity.pl/podatek-pit-od-kryptowalut/)
- [Poradnik Przedsiębiorcy — Rozliczenie straty z akcji](https://poradnikprzedsiebiorcy.pl/-rozliczenie-straty-z-akcji-jakie-sa-zasady-rozliczania)
- [Poradnik Przedsiębiorcy — Rozliczenie straty podatkowej z lat ubiegłych](https://poradnikprzedsiebiorcy.pl/-rozliczenie-straty-podatkowej-z-lat-ubieglych-warunki-odliczania)
- [nex.katowice.pl — Czy stratę z akcji można rozliczyć z dochodem z kryptowalut](https://www.nex.katowice.pl/post/czy-strat%C4%99-z-akcji-mo%C5%BCna-rozliczy%C4%87-z-dochodem-z-kryptowalut)
- [podatekgieldy.pl — Strata z giełdy](https://podatekgieldy.pl/pl/strata-z-gieldy-pit-38)
- [podatekgieldy.pl — Kompletny przewodnik PIT-38](https://podatekgieldy.pl/en/przewodnik-pit-38)
- [pit.pl — Rozliczenie straty podatkowej](https://www.pit.pl/strata/)
- [Koinly — Poland Crypto Tax Guide](https://koinly.io/guides/crypto-tax-poland/)
- [prawo.pl — Obrót walutami wirtualnymi interpretacja KIS](https://www.prawo.pl/podatki/obrot-walutami-wirtualnymi-interpretacja,515844.html)
- [Lexlege — art. 30b ustawy o PIT](https://lexlege.pl/ustawa-o-podatku-dochodowym-od-osob-fizycznych/art-30b/)
- [arslege.pl — art. 9 ustawy o PIT](https://arslege.pl/zakres-opodatkowania-dochodow/k71/a18841/)
- [podatki.gov.pl — PIT-38 za 2025 rok](https://www.podatki.gov.pl/twoj-e-pit/pit-38-za-2025-rok/)
- [saregofinance.pl — PIT-38 dla brokerów zagranicznych](https://saregofinance.pl/pit-38/)

### Interpretacje podatkowe

- Interpretacje Dyrektora KIS dot. art. 22 ust. 16 — potwierdzenie że nadwyżka
  kosztów z krypto przenosi się na kolejne lata bez limitu czasowego
  (wykładnia celowościowa)
