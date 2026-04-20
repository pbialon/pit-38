# Tax Law Compliance Audit — PIT-38 Calculator

Audit of the pit-38 tax calculator against Polish tax law (ustawa o PIT, art. 30b).
Performed April 2026.

---

## Summary

| # | Issue | Severity | Tax Impact | Status |
|---|-------|----------|------------|--------|
| 1 | Wrong exchange rate for partial sell cost | **CRITICAL** | Over/underpayment | **FIXED** (PR #37) |
| 2 | No 5-year limit on loss deduction | **CRITICAL** | Underpayment if old losses | **FIXED** (PR #38) |
| 3 | Crypto cost method — now explicitly correct | OK | None | **FIXED** (PR #38) |
| 4 | OperationType vs Action type mismatch | Low | None currently | Open |
| 5 | Stock split handling | **CORRECT** | — | — |
| 6 | NBP table "a" | **CORRECT** | — | — |
| 7 | Day-minus-one rule | **CORRECT** | — | — |
| 8 | 19% tax rate | **CORRECT** | — | — |
| 9 | FIFO method | **CORRECT** | — | — |
| 10 | Polish holidays | **CORRECT** | — | — |
| 11 | Rounding to full PLN | Minor | Cosmetic | Open |
| 12 | Dividend withholding tax | Moderate | Under/overpayment | Open |
| 13 | Commission fees | Low | Depends on broker | Open (likely non-issue) |

---

## Critical Bugs

### 1. ~~Wrong exchange rate date for partial sell cost~~ — FIXED

**Status:** Fixed in PR #37 (commit `12c9381`).

Changed `transaction.date` → `oldest_buy.date` on line 67 of
`per_stock_calculator.py`. Added `DateAwareExchanger` test helper and
`test_partial_sell_uses_buy_date_exchange_rate` test that catches this bug.

---

### 2. ~~Deductible loss has no 5-year limit~~ — FIXED

**Status:** Fixed in PR #38 (commit `02123ee`).

Split `TaxCalculator` into `StockTaxCalculator` (5-year limit, 50% cap,
one-time ≤5M PLN for post-2018 losses) and `CryptoTaxCalculator` (unlimited
carry-forward per art. 22 ust. 16). Added `LossRecord` value object for
per-year loss tracking with individual expiry dates and 50% ceilings.

---

## Moderate Issues

### 3. ~~Crypto cost calculation — accidentally correct~~ — FIXED

**Status:** Fixed in PR #38. Now **explicitly** correct — `CryptoTaxCalculator`
is a separate class that implements art. 22 ust. 16 (unlimited cost surplus
carry-forward) without any of the stock-specific limits.

---

### 4. Dividend taxation — withholding tax not accounted for

**File:** `src/domain/stock/profit/profit_calculator.py:54-60`

Dividends are treated as pure income. The output says:
```
"Dividends (if you paid 30% in USA you don't have to pay)"
```

**Polish tax law and PL-US tax treaty:**
- With W-8BEN: 15% US withholding → you still owe 4% in Poland (19% - 15%)
- Without W-8BEN: 30% US withholding → you owe 0% in Poland (can't reclaim excess 11%)

The code doesn't track withholding tax at all. Someone who filed W-8BEN would still owe 4% Polish tax, but the tool doesn't calculate this.

---

### 5. Type mismatch: OperationType vs Action

**File:** `src/plugins/stock/revolut/transaction_row_parser.py:33`

```python
action=cls._operation_type(row),  # Returns OperationType, not Action
```

The `Transaction` constructor expects `action: Action` (BUY/SELL enum), but `_operation_type()` returns `OperationType`. This works because `Action.__eq__` compares `.value` strings, and both `Action.BUY` and `OperationType.BUY` have value `"BUY"`. Fragile but no tax impact.

---

## What's Correct

### NBP exchange rate table (table "a")
**Art. 11a ust. 1 ustawy o PIT** requires the average NBP rate ("kurs średni"). Table "a" provides exactly this. ✓

### "Day minus one" rule
The `Exchanger.get_day_one()` method correctly subtracts 1 day and skips back over weekends and Polish holidays to find the last business day before the transaction. ✓

### 19% flat tax rate
**Art. 30b ust. 1** — 19% for capital gains income. ✓

### FIFO method for stocks
The `Queue` + `PerStockProfitCalculator` correctly implements FIFO matching of BUY→SELL per stock symbol. ✓

### Polish holidays calendar
Uses `holidays.Poland()` library to correctly identify Polish public holidays. ✓

### Stock split handling
Multiplies share quantity while preserving total cost basis — correct. ✓

---

## Minor / Nice-to-have

### Rounding to full PLN
PIT-38 form requires integer PLN amounts (art. 63 §1 Ordynacji podatkowej). The code outputs amounts with decimal precision. Users must round manually when filling the form.

### Commission/brokerage fees
The code tracks `SERVICE_FEE` (custody fees) as costs but doesn't separately extract per-transaction commissions. For Revolut, the "Total Amount" field likely already includes commission, so this may be a non-issue.

---

## Remaining Issues

1. **#4** — OperationType vs Action type mismatch (Low — works by coincidence, fragile)
2. **#11** — Rounding to full PLN (Minor — cosmetic, users round manually)
3. **#12** — Dividend withholding tax (Moderate — needs W-8BEN status tracking)
4. **#13** — Commission fees (Low — likely already in Revolut's Total Amount)
