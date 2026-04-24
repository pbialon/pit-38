# Tax Law Compliance Audit — PIT-38 Calculator

Audit of the pit-38 tax calculator against Polish tax law (ustawa o PIT, art. 30b).
Performed April 2026.

---

## Summary

| # | Issue | Severity | Tax Impact | Status |
|---|-------|----------|------------|--------|
| 1 | OperationType vs Action type mismatch | Low | None currently | ✅ Resolved (#53) |
| 2 | Rounding to full PLN | Minor | Cosmetic | Open (#52) |
| 3 | Dividend withholding tax | Moderate | Under/overpayment | Open (#51) |
| 4 | Commission fees | Low | Depends on broker | Open |

## What's Correct

- **NBP exchange rate table "a"** — art. 11a ust. 1 ✓
- **Day-minus-one rule** — `Exchanger.get_day_one()` ✓
- **19% flat tax rate** — art. 30b ust. 1 ✓
- **FIFO method** — `Queue` + `PerStockProfitCalculator` ✓
- **Polish holidays** — `holidays.Poland()` ✓
- **Stock split handling** — quantity adjustment preserving cost basis ✓
- **Partial sell exchange rate** — uses buy date, not sell date ✓
- **5-year loss deduction limit** — `StockTaxCalculator` with `LossRecord` ✓
- **50% cap / 5M PLN one-time** — pre-2019 vs post-2019 rules ✓
- **Crypto cost carry-forward** — `CryptoTaxCalculator`, unlimited per art. 22 ust. 16 ✓
- **Stock/crypto source separation** — separate tax calculators ✓

---

## Open Issues

### 1. OperationType vs Action type mismatch ✅ RESOLVED

Resolved by splitting the responsibility into two enums with clear roles (see #53):

- `Action(BUY, SELL)` — the transactional action, attribute of `Transaction`.
  Common to stocks and crypto.
- `StockMarketOperation(BUY, SELL, DIVIDEND, SERVICE_FEE, STOCK_SPLIT)` —
  classifier for rows in a stock-market CSV. Stock-specific; crypto CSV uses
  `Action` directly.

Silent `.value`-based coercion from `OperationType` to `Action` in the stock
factory is replaced by an explicit `StockMarketOperation.to_action()` method
that raises for non-transactional values.

### 2. Rounding to full PLN

PIT-38 form requires integer PLN amounts (art. 63 §1 Ordynacji podatkowej).
The code outputs amounts with decimal precision. Users must round manually.

### 3. Dividend withholding tax

Dividends are shown as pure income without withholding tax offset.

- With W-8BEN: 15% US withholding → 4% additional Polish tax (19% - 15%)
- Without W-8BEN: 30% US withholding → 0% Polish tax

### 4. Commission fees

`SERVICE_FEE` (custody fees) tracked as costs. Per-transaction commissions
likely already included in Revolut's `Total Amount` — probably a non-issue.
