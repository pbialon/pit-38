# Broker-specific guides

Per-broker notes that don't belong in the README but matter when you're
importing a specific broker's export for the first time. One section per
broker; see the top-level `README.md` for the supported-brokers table.

## IBI Capital

IBI Capital is an Israeli trustee broker that administers equity
compensation (RSU + ESPP) plans for employees of companies listed on
NASDAQ/NYSE. The `pit38 import ibi-capital` command parses IBI's **Sale
Of Stock Activity Statement** PDFs — one PDF per executed sale order —
and emits standardized transactions plus service fees.

### Scope — what this plugin does and doesn't

**Does**:
- Parses every `*.pdf` Sale Of Stock Activity Statement under the paths
  you pass via `-i` (files or directories, repeatable).
- Emits one synthetic `BUY` dated at the grant day, one `SELL` dated at
  the execution day, and one `SERVICE_FEE` at the execution day when
  total fees are non-zero.
- Looks up the company's ticker in a packaged JSON seed
  (`pit38/plugins/stock/ibi_capital/companies.json`); `--ticker` overrides.

**Doesn't**:
- Read vesting confirmations, ESPP purchase reports, dividend statements,
  or any non-sale IBI document.
- Automatically handle currencies other than USD (all sample PDFs were
  USD — if you have a non-USD order, open an issue).

### Usage

Download your order confirmations from the IBI Capital portal into a
folder, then:

```bash
pit38 import ibi-capital -i ~/Downloads/ibi_orders/ -o ibi.csv
pit38 stock -f ibi.csv -y 2025
```

You can mix IBI output with exports from other brokers:

```bash
pit38 stock -f ibi.csv -f revolut.csv -y 2025
```

Use `--ticker MYSYM` to override the company→ticker mapping (useful when
your company isn't in the shipped `companies.json` yet).

### Cost basis — RSU vs ESPP

IBI's order PDFs expose a `Price For Tax` field that the plugin uses as
the per-share cost basis for the synthetic `BUY` transaction:

- **RSU** (typical grant): `Price For Tax: USD 0.00`. The plugin emits
  `BUY` with `fiat_value = 0`. This follows the conservative/KIS line of
  Polish tax interpretation: for shares received via RSU the employee
  did not bear an acquisition cost, and the value at vest was already
  taxed as income from employment. The capital gain on sale is therefore
  `proceeds − 0 − fees`.
- **ESPP** (employee stock purchase plan): `Price For Tax: USD N.NN`
  reflects the discounted purchase price you actually paid. The plugin
  uses that as the cost basis — `BUY` `fiat_value = shares × Price For Tax`.

This is an interpretation of tax law, not a universal rule. If your own
advisor takes a different position (e.g. allowing the FMV-at-vest as RSU
cost basis), edit the resulting CSV directly — each `BUY` row's
`fiat_value` column is straightforward to adjust.

### Adding a new company → ticker mapping

If your company name isn't in the seed, you have two options:

1. **Quick fix** — pass `--ticker MYSYM` on the CLI; the plugin uses it
   for every PDF in that run.
2. **Permanent fix** — open a PR adding a line to
   [`pit38/plugins/stock/ibi_capital/companies.json`](../pit38/plugins/stock/ibi_capital/companies.json).
   Keys are the `Company:` value **exactly as it appears in your IBI
   PDFs** (lowercase — the loader does case-insensitive lookup, but
   keeping the file lowercase keeps diffs clean). Values are current
   NASDAQ/NYSE tickers in uppercase.

### Known limitations

- The plugin assumes USD throughout. Non-USD orders would need a
  `Currency` enum extension (ILS/EUR support isn't there yet).
- `Wire Fee` from the `Funds Proceed` section isn't surfaced separately.
  In the sample PDFs it's always `0.00`; if you hit a non-zero wire fee
  that matters for your tax calc, open an issue.
- Anonymized PDF fixtures aren't shipped in the repo (real IBI PDFs
  contain PII). Parser unit tests use anonymized text snapshots under
  `tests/e2e/fixtures/ibi_order_fake_*.txt`.
