---
name: "\U0001F1F5\U0001F1F1 Prośba o obsługę brokera"
about: Poproś o wsparcie nowego brokera lub zgłoś zmianę formatu CSV
title: "[BROKER] "
labels: ["broker-support", "help wanted"]
---

<!-- Użyj tego szablonu gdy:
     - Twój broker nie jest na liście wspieranych i chcesz żeby został dodany
     - Obecnie wspierany broker zmienił format CSV i pit-38 przestał działać
     Dla ogólnej dyskusji zacznij od Discussions → Broker support. -->

## Broker

- **Nazwa**:
- **Region** (US / EU / PL / inny):
- **Klasa aktywów** (akcje / krypto / oba):
- **Strona** (pomocna dla znalezienia dokumentacji formatu):

## Zanonimizowany sample eksportu

<!-- ⚠️ UWAGA: najpierw usuń wszystkie dane osobowe — numery kont, nazwiska, itp.
     Wklej 5-10 wierszy pokrywających typowe typy operacji od brokera.
     Jeśli plik jest szeroki, link do gista jest w porządku. -->

```csv
wklej tutaj zanonimizowany CSV
```

## Typowe kolumny

<!-- Skopiuj wiersz nagłówkowy CSV dosłownie. Te kolumny pit-38 musi sparsować. -->

## Zaobserwowane typy operacji

<!-- Wymień unikalne wartości w kolumnie "Type"/"Operation". Przykłady:
     Revolut używa "BUY - MARKET", "SELL - LIMIT", "DIVIDEND", "CUSTODY FEE",
     "STOCK SPLIT", "CASH WITHDRAWAL", itp. -->

## Znane kwirki

<!-- Coś niestandardowego? Przykłady:
     - Kodowanie inne niż UTF-8 lub BOM
     - Europejski format liczb (1.234,56) lub spacja jako separator tysięcy
     - Pozycja znaku minus (USD -0.07 vs -USD 0.07)
     - Zlokalizowane nazwy kolumn (PL/DE/itp.)
     - Wiele arkuszy (eksport Excel) -->

## Zakres lat podatkowych

<!-- Jakie lata podatkowe obejmuje Twój sample? Starsze formaty mogą się różnić. -->

## Czy możesz pomóc w implementacji?

- [ ] Chcę napisać plugin samodzielnie (dokumentacja pluginu nadchodzi — patrz #49, #50)
- [ ] Mogę dostarczyć dane testowe, ale nie kod
- [ ] Tylko prośba

## Dodatkowy kontekst

<!-- Linki do dokumentacji API brokera, powiązanych issues, wcześniejszych
     projektów GitHub dla tego brokera, itp. -->
