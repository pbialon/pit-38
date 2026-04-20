# Polish Capital Gains Tax Rules — PIT-38

> **[🇵🇱 Wersja polska](TAX_RULES.pl.md)**

This document describes the tax rules implemented by the pit-38 calculator,
based on the Polish Personal Income Tax Act (ustawa z dnia 26 lipca 1991 r.
o podatku dochodowym od osób fizycznych, Dz.U.2025.163 consolidated text).

Last updated: April 2026.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Tax Rate](#2-tax-rate)
3. [Currency Conversion — NBP Rates](#3-currency-conversion)
4. [FIFO Method for Stocks](#4-fifo-method)
5. [Loss Deduction — Stocks](#5-loss-deduction--stocks)
6. [Cost Carry-Forward — Crypto](#6-cost-carry-forward--crypto)
7. [Source Separation — Stocks vs Crypto](#7-source-separation)
8. [Transitional Rules](#8-transitional-rules)
9. [Dividends](#9-dividends)
10. [Sources](#10-sources)

---

## 1. Overview

PIT-38 is the Polish annual tax return for capital gains income. It covers:

- Sale of **securities** (stocks, bonds, ETFs) — art. 30b sec. 1
- Sale of **derivative instruments** (options, futures) — art. 30b sec. 1
- Sale of **shares** in companies — art. 30b sec. 1
- Redemption of **investment fund units** (from 2024) — art. 30b sec. 1 pt 5
- Sale of **virtual currencies** (crypto) — art. 30b sec. 1a

Filing deadline: **April 30** of the year following the tax year.
You must file PIT-38 even if you incurred a loss (to preserve deduction rights).

---

## 2. Tax Rate

**19% flat rate** on capital gains (art. 30b sec. 1, 1a).

Tax = max(0, taxable_base × 0.19)

Where `taxable_base = income − cost − deductible_losses_from_prior_years`.

---

## 3. Currency Conversion

### Legal basis: art. 11a sec. 1

Foreign currency amounts must be converted to PLN using the **average NBP
exchange rate** (National Bank of Poland, table "a") from the **last business
day preceding** the transaction date.

### Implementation

- "Business day" excludes weekends (Saturday, Sunday) and Polish public holidays
- If the day before the transaction is not a business day, go further back
- Example: transaction on Monday Jan 3 → use rate from Friday Dec 31
  (unless Dec 31 is a holiday, then Dec 30, etc.)

The `Exchanger.get_day_one()` method implements this rule.

---

## 4. FIFO Method

### Legal basis: art. 30a sec. 3

When selling securities, the cost of acquisition is determined using the
**FIFO method** (First In, First Out). The shares purchased earliest are
matched against the sale first.

### Implementation

Each stock ticker has its own FIFO queue. When selling:
1. Match against the oldest buy position
2. If the sell exhausts the buy position, move to the next
3. If a partial sell, split the buy position proportionally
4. Cost is converted to PLN at the NBP rate from the **buy date**
   (not the sell date)

The `PerStockProfitCalculator` with `Queue` implements this.

---

## 5. Loss Deduction — Stocks

### Legal basis: art. 9 sec. 3

Losses from capital gains (stocks, bonds, derivatives, investment funds) can
be deducted from income of the **same source** in the next **5 consecutive
tax years**.

### Two methods (for losses from 2019 onwards)

#### Method 1 — Gradual deduction

Deduct up to **50% of the loss amount** per year, spread over up to 5 years.

Example: 100,000 PLN loss in 2022
- 2023: deduct up to 50,000 PLN
- 2024: deduct up to 50,000 PLN
- ... up to 2027 (5 years from 2022)

#### Method 2 — One-time deduction up to 5,000,000 PLN

Deduct the full loss (up to 5M PLN) in a single year. Any remainder above
5M follows the 50% annual cap in the remaining years.

**Practical simplification**: For losses under 5M PLN incurred from 2019
onwards, the one-time option means **the full loss can be deducted at once**
without worrying about the 50% cap. The 50% cap only applies when:
- The loss was incurred in 2018 or earlier (old rules), OR
- The loss exceeds 5,000,000 PLN

### Constraints

- **5-year window**: loss from year X expires after year X+5
- **Same source only**: stock losses cannot offset crypto income
- **Must file PIT-38**: even in loss years, to preserve future deduction rights

---

## 6. Cost Carry-Forward — Crypto

### Legal basis: art. 22 sec. 16

Cryptocurrencies use a **different mechanism** than stocks. There is no
"loss deduction" — instead, the **surplus of costs over income** in a tax
year increases the costs for the **following tax year**.

> "The surplus of costs of obtaining income over income from the paid disposal
> of virtual currency obtained in the tax year increases the costs of obtaining
> income from the paid disposal of virtual currency incurred in the following
> tax year."

### Key differences from stocks

| Feature | Stocks (art. 9 sec. 3) | Crypto (art. 22 sec. 16) |
|---------|------------------------|--------------------------|
| Mechanism | Loss deduction | Cost surplus carry-forward |
| Time limit | 5 years | **None** (*) |
| Annual cap | 50% of loss | **None** |
| One-time option | Up to 5M PLN | N/A |

(*) The literal text says "following tax year" (singular), but the Director
of KIS (National Tax Information) confirmed in interpretations that cost
surplus carries forward to **subsequent years without time limit**
(purposive interpretation).

### Filing obligation

Per art. 30b sec. 6a, you must file PIT-38 **even if you had no crypto
income** but incurred acquisition costs. This ensures costs are declared
and can be carried forward.

---

## 7. Source Separation

### Legal basis: art. 30b sec. 5d, art. 9 sec. 3a pt 2

Income from virtual currencies **cannot be combined** with other income
taxed under art. 30b (securities, derivatives, etc.).

| Loss from → | Offset against ↓ | Allowed? |
|-------------|------------------|----------|
| Stocks | Stocks / Bonds / Derivatives | **Yes** |
| Stocks | Investment funds (from 2024) | **Yes** |
| Stocks | Crypto | **No** |
| Crypto | Crypto | **Yes** |
| Crypto | Stocks | **No** |

All non-crypto instruments belong to the same income source ("monetary
capital" under art. 30b sec. 1), so losses from one type can offset
income from another within that source.

---

## 8. Transitional Rules

### Pre-2019 vs post-2019 losses

The amendment of November 9, 2018 introduced the one-time deduction option
(method 2). It applies to losses incurred in tax years starting after
December 31, 2018 — i.e., from 2019 onwards.

| Loss year | Available methods | Deduction period |
|-----------|-------------------|-----------------|
| ≤ 2018 | 50% annual cap only | 5 years from loss |
| ≥ 2019 | 50% cap **or** one-time up to 5M PLN | 5 years from loss |

As of 2026, the oldest deductible loss is from **2021** (deductible 2022–2026).

### Investment funds (from 2024)

Starting 2024, income from investment fund unit redemptions is self-reported
on PIT-38 (previously, the fund withheld tax). This means:
- Fund losses can now offset stock gains and vice versa
- Losses from funds incurred **before 2024** cannot be deducted

---

## 9. Dividends

### Overview

Dividends from foreign stocks (e.g., US stocks via Revolut) are subject
to withholding tax under bilateral tax treaties.

**US stocks with W-8BEN form**: 15% US withholding → 4% additional Polish
tax (19% - 15%). Without W-8BEN: 30% US withholding → 0% Polish tax
(excess cannot be reclaimed).

The calculator currently shows dividend income but does not compute
withholding tax offsets. This is informational only.

---

## 10. Sources

### Legislation

- Personal Income Tax Act of July 26, 1991 (Dz.U.2025.163 consolidated text)
  — art. 9 sec. 3, art. 11a sec. 1, art. 22 sec. 16, art. 30b

### Tax portals

- [Stockbroker.pl — Loss deduction guide](https://stockbroker.pl/jak-rozliczac-straty-z-lat-ubieglych-2025/)
- [e-pity.pl — Crypto tax](https://www.e-pity.pl/podatek-pit-od-kryptowalut/)
- [Poradnik Przedsiębiorcy — Stock loss settlement](https://poradnikprzedsiebiorcy.pl/-rozliczenie-straty-z-akcji-jakie-sa-zasady-rozliczania)
- [podatekgieldy.pl — Stock exchange losses](https://podatekgieldy.pl/pl/strata-z-gieldy-pit-38)
- [podatekgieldy.pl — Complete PIT-38 guide](https://podatekgieldy.pl/en/przewodnik-pit-38)
- [Koinly — Poland Crypto Tax Guide](https://koinly.io/guides/crypto-tax-poland/)
- [Lexlege — art. 30b PIT Act](https://lexlege.pl/ustawa-o-podatku-dochodowym-od-osob-fizycznych/art-30b/)
- [podatki.gov.pl — PIT-38 for 2025](https://www.podatki.gov.pl/twoj-e-pit/pit-38-za-2025-rok/)
- [saregofinance.pl — PIT-38 for foreign brokers](https://saregofinance.pl/pit-38/)

### Tax interpretations

- Director of KIS interpretations on art. 22 sec. 16 — confirming unlimited
  time carry-forward of crypto cost surplus (purposive interpretation)
