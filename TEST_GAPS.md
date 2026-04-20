# Test Coverage Gaps

Analysis of missing test coverage, cross-referenced with [TAX_LAW_AUDIT.md](TAX_LAW_AUDIT.md).

---

## Critical

### 1. Partial sell uses wrong exchange rate — hidden by StubExchanger

**Audit ref:** TAX_LAW_AUDIT.md #1

`StubExchanger` returns a fixed 4.0 rate regardless of date, so tests never catch
the bug in `per_stock_calculator.py:66-67` where partial sell cost is exchanged at
the SELL date instead of the BUY date.

**Missing test:** A `PerStockProfitCalculator` test with an exchanger that returns
different rates per date, using a partial sell (e.g., buy 10 shares, sell 3).

**File:** `tests/test_per_stock_calculator.py`

### 2. No test for partial sell at all

All existing tests sell entire positions or exact sums (buy 3x1 → sell 3).
No test exercises the `else` branch in `_calculate_cost_for_sell` (lines 64-70),
where the sell amount is less than the oldest buy position.

**Missing test:** `buy(apple(10), ...) → sell(apple(3), ...)` — verify cost is
proportional and remaining 7 shares stay in the queue.

**File:** `tests/test_per_stock_calculator.py`

---

## High

### 3. No 5-year limit on deductible losses

**Audit ref:** TAX_LAW_AUDIT.md #2

No test verifies that losses older than 5 years are excluded from deduction.
Current tests span only 2-4 years.

**Missing test:** Loss in 2015, profit in 2022 → loss should NOT be deductible.

**Note:** This test should be written to *fail* against current code, proving the
bug exists, then the limit should be implemented to make it pass.

**File:** `tests/test_tax.py`

### 4. Tax amount (19%) is never asserted

Tests check `base_for_tax` but never check the `tax` field. The 19% calculation
(`TaxCalculator.calculate_tax`) is untested.

**Missing test:** Verify `tax == base_for_tax * 0.19` when profitable, and `tax == 0`
when base_for_tax is negative.

**File:** `tests/test_tax.py`

### 5. No test: tax = 0 when loss

No assertion that when `base_for_tax < 0`, the resulting `tax` is `0 PLN` (not negative).

**File:** `tests/test_tax.py`

---

## Medium

### 6. Crypto: only 1 test, minimal scenario

`test_crypto_profit_calculator.py` has a single test with a simple buy/sell-each-year
pattern. Missing scenarios:

- Buy in year X, sell in year X+1 (cost carry-forward)
- Buy without any sell (cost only, zero income)
- Multiple cryptocurrencies in the same dataset (BTC + ETH)

**File:** `tests/test_crypto_profit_calculator.py`

### 7. Exchanger: no test with Polish holidays

`test_exchanger.py` tests weekends but not holidays. Missing:

- Transaction the day after a Polish holiday (e.g., Nov 12 when Nov 11 is
  Independence Day) — rate should come from Nov 10 or earlier
- Transaction on Jan 2 when Jan 1 is a holiday and Dec 31 is a Friday —
  rate should come from Dec 30

**File:** `tests/test_exchanger.py`

---

## Low

### 8. No test: sell without prior buy raises error

`_calculate_cost_for_sell` raises `ValueError("No buy transaction to match sell
transaction")` but no test verifies this behavior.

**File:** `tests/test_per_stock_calculator.py`

### 9. No test: manual deductible_loss CLI parameter

`TaxCalculator.calculate_tax_per_year()` accepts `deductible_loss` which overrides
automatic calculation when != -1. This code path is untested.

**File:** `tests/test_tax.py`

### 10. Assertion bug in _get_company_name

`per_stock_calculator.py:45` uses `assert (generator_expression)` which always
evaluates to `True` (a generator is truthy). Should be `assert all(...)`.
Same issue in `stock_split_handler.py:59-60`.

**File:** `pit38/domain/stock/profit/per_stock_calculator.py`,
`pit38/domain/stock/profit/stock_split_handler.py`
