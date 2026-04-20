# Tax Law Compliance Audit — PIT-38 Calculator

Audit of the pit-38 tax calculator against Polish tax law (ustawa o PIT, art. 30b).
Performed April 2026.

---

## Summary

| # | Issue | Severity | Tax Impact |
|---|-------|----------|------------|
| 1 | Wrong exchange rate for partial sell cost | **CRITICAL** | Over/underpayment |
| 2 | No 5-year limit on loss deduction | **CRITICAL** | Underpayment if old losses |
| 3 | Crypto cost method — accidentally correct | OK (for now) | None |
| 4 | OperationType vs Action type mismatch | Low | None currently |
| 5 | Stock split handling | **CORRECT** | — |
| 6 | NBP table "a" | **CORRECT** | — |
| 7 | Day-minus-one rule | **CORRECT** | — |
| 8 | 19% tax rate | **CORRECT** | — |
| 9 | FIFO method | **CORRECT** | — |
| 10 | Polish holidays | **CORRECT** | — |
| 11 | Rounding to full PLN | Minor | Cosmetic |
| 12 | Dividend withholding tax | Moderate | Under/overpayment |
| 13 | Commission fees | Low | Depends on broker |

---

## Critical Bugs

### 1. Wrong exchange rate date for partial sell cost

**File:** `src/domain/stock/profit/per_stock_calculator.py:66-67`

When a SELL transaction only partially consumes a BUY position, the code uses the **SELL date** for currency exchange instead of the **BUY date**:

```python
# Line 66-67 — BUG: uses transaction.date (SELL date) instead of oldest_buy.date (BUY date)
cost += self.exchanger.exchange(
    transaction.date, oldest_buy.fiat_value) * ratio_of_oldest_buy_to_include
```

Compare with the correct branch (line 61) which correctly uses `oldest_buy.date`:
```python
cost += self.exchanger.exchange(oldest_buy.date, oldest_buy.fiat_value)
```

**Polish tax law (art. 23 ust. 1 pkt 38 ustawy o PIT):** The cost of acquisition (koszt uzyskania przychodu) must be converted to PLN at the NBP rate from the business day preceding the **purchase date**, not the sale date.

**Impact:** If USD/PLN changed between buy and sell dates, the calculated tax will be incorrect. This could cause either overpayment or underpayment of tax.

**Fix:** Change `transaction.date` to `oldest_buy.date` on line 67.

**Why tests don't catch this:** The `StubExchanger` in tests returns a fixed 4.0x rate regardless of date, so both dates produce the same result.

---

### 2. Deductible loss has no 5-year limit

**File:** `src/domain/tax_service/tax_calculator.py:35-48`

The code has a `# todo: up to 5 years (?)` comment acknowledging this issue but it's not implemented. The method `deductible_loss_from_previous_years()` accumulates losses from **all** previous years without any time limit.

**Polish tax law (art. 9 ust. 3 ustawy o PIT):** Losses can only be deducted within the **5 following tax years**. A loss from 2018 cannot be deducted in 2024 or later.

Additionally, since 2019 there's a rule that in a single year you can deduct either:
- up to 50% of the loss from a given year, OR
- the full amount if the loss was ≤ 5,000,000 PLN

The code implements neither the 5-year limit nor the 50%/5M PLN per-year cap.

**Impact:** If someone has losses from >5 years ago, the tool would incorrectly deduct them, leading to underpayment of tax.

**Important caveat for crypto:** For cryptocurrency (art. 30b ust. 1a), the cost carry-forward rules are different — unrealized costs carry forward **without** the 5-year or 50% limitations. The current code accidentally produces the right result for crypto because it applies no limits at all. If you fix this for stocks, you must NOT apply the 5-year limit to crypto.

---

## Moderate Issues

### 3. Crypto cost calculation — accidentally correct

**File:** `src/domain/crypto/profit_calculator.py`

The crypto calculator sums all BUYs as cost and all SELLs as income per year, without FIFO matching. For crypto under Polish tax law, this is actually the correct approach — costs are recognized in the year they're incurred, and any excess carries forward. The `TaxCalculator`'s loss accumulation mechanism handles the carry-forward.

However, this only works correctly because the missing 5-year limit (bug #2) happens to be the correct behavior for crypto. Fixing bug #2 requires separating the stock and crypto code paths.

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

## Recommended Fix Priority

1. **Bug #1** — partial sell exchange rate (one-line fix: `transaction.date` → `oldest_buy.date`)
2. **Bug #2** — 5-year deductible loss limit (requires separating stock vs crypto tax logic)
3. **Feature #4** — dividend withholding tax tracking
