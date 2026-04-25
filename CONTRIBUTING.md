# Contributing to pit-38

Thanks for your interest. `pit-38` is an open-source tax calculator people
rely on to file real PIT-38 declarations, so correctness matters more than
speed. Friendly code review is how we get there — first-time contributors
are very welcome.

Discussions and PR reviews happen in **English or Polish** — use whichever
you're more comfortable with. The code and docs are primarily English so
that international contributors can participate, but tax rules are Polish
and forum links are usually Polish, so both languages coexist here
naturally.

> **[🇵🇱 Wersja polska niedługo](https://github.com/pbialon/pit-38/issues)** —
> jeśli wolisz pisać po polsku, śmiało otwieraj issue / PR po polsku.
> Odpiszemy w Twoim języku.

---

## Table of contents

- [Quick start](#quick-start)
- [Prerequisites](#prerequisites)
- [Development setup](#development-setup)
- [Running tests](#running-tests)
- [Linting and style](#linting-and-style)
- [Submitting a pull request](#submitting-a-pull-request)
- [Adding a new broker plugin](#adding-a-new-broker-plugin)
- [Reporting tax-law bugs](#reporting-tax-law-bugs)
- [Code of Conduct](#code-of-conduct)
- [Where to ask questions](#where-to-ask-questions)

---

## Quick start

```bash
git clone https://github.com/pbialon/pit-38
cd pit-38
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

If that passes, you have a working dev environment. Skip to
[Submitting a pull request](#submitting-a-pull-request) if you already know
what you want to change, or read on for details.

## Prerequisites

- **Python 3.10+** — the code uses `X | Y` union syntax and other 3.10
  features. Earlier versions won't work.
- **git** — for cloning and branching.
- **pipx** (optional) — only needed if you want to install `pit-38` as a
  CLI tool; not required for development.

## Development setup

Use a virtualenv so the editable install and its dev dependencies don't
pollute your system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The `[dev]` extra installs `pytest`, `flake8`, and `coverage` (see
`pyproject.toml`). After install, `pit38` is available on your `PATH` and
points at the checkout, so your edits are picked up without reinstalling.

Sanity check:

```bash
pit38 --help
```

## Running tests

The full suite runs in seconds:

```bash
pytest tests/
```

End-to-end tests, which exercise the CLI against real anonymized CSV
fixtures, live under `tests/e2e/`:

```bash
pytest tests/e2e/
```

With coverage:

```bash
pytest tests/ --cov=pit38 --cov-branch
```

**Test conventions** (worth matching when you add tests):

- Tests use `unittest.TestCase` — not pytest fixtures.
- Helpers live in `tests/utils.py` — factory functions like `buy()`,
  `sell()`, `apple()`, `usd()`, `zl()`, and `StubExchanger` (fixed 4.0
  USD→PLN). Prefer these over hand-rolled objects.
- If you change tax-calculation behaviour, update or add an E2E fixture
  that shows the change end-to-end.

## Linting and style

Flake8 runs in CI with a minimal config — only syntax errors and
undefined names fail the build (E9, F63, F7, F82). We deliberately keep
the bar low here so style nitpicks don't stall contributions. Run it
locally if you want:

```bash
flake8 pit38/ tests/ --select=E9,F63,F7,F82
```

General code style:

- Follow patterns already present in the module you're editing. When in
  doubt, mirror the neighbouring file.
- No new abstractions unless the task requires them. Three similar lines
  beat a premature helper.
- Type hints are encouraged on public functions but not required.

## Submitting a pull request

1. **Fork and branch.** Branch names roughly follow the pattern
   `<type>/<issue-number>-<short-slug>`:
   - `fix/33-revolut-csv-bom`
   - `feat/9-csv-loader-consolidation`
   - `docs/46-contributing`
   - `refactor/...`, `test/...`, `chore/...`

2. **Commit style.** Terse, imperative mood, present tense. First line
   under ~72 chars. Include the issue number when closing one:
   ```
   fix: Revolut CSV with BOM, lowercase headers, and unknown operations (#33)
   ```
   Longer rationale goes in the body. Look at `git log` for tone.

3. **Link to the issue.** In the PR body, put `Closes #<n>` so the issue
   auto-closes on merge. If there's no issue yet and the change is
   non-trivial, open one first — reviewers like having the "why"
   captured somewhere durable.

4. **Use the PR template.** `.github/PULL_REQUEST_TEMPLATE.md` asks
   specifically about tax-correctness impact. Fill it in honestly — even
   "purely refactor, no tax impact" is a valid answer and saves reviewer
   time.

5. **Keep PRs focused.** One issue per PR, ideally. If you find
   tangential bugs while working, file them as separate issues rather
   than bundling.

6. **Expect review.** For anything that touches tax output, expect a
   careful pass. Reviewers may ask for references to the *ustawa*
   article (the Polish income tax act) or ask you to add a regression
   fixture.

## Adding a new broker plugin

Broker plugins live under `pit38/plugins/` and transform a broker-specific
CSV export into the standardized format that `pit38` consumes. Each
plugin is self-contained. See
[`pit38/plugins/README.md`](pit38/plugins/README.md) for the plugin
architecture overview (PL/EN).

**Reference implementations** (read these first):

- **Stocks** — `pit38/plugins/stock/revolut/` (most complete, handles
  BOM, unknown operations, dividends, fees, stock splits)
- **Crypto** — `pit38/plugins/crypto/binance/`

**High-level recipe:**

1. Create `pit38/plugins/stock/<broker>/` (or `crypto/<broker>/`).
2. Implement an entry point (`__main__.py` or a CLI command) that
   accepts `--input-path` and `--output-path`.
3. Parse the broker's export, emit rows in the standardized CSV shape
   (see `pit38/data_sources/stock_loader/example_format.csv` or
   `pit38/data_sources/crypto_loader/example_format.csv`).
4. Share number/currency parsing via
   `pit38.plugins.normalization` (`normalize_currency_layout`,
   `parse_amount`) rather than re-rolling regex. Revolut and E*Trade
   both use it — new plugins should too.
5. Add the broker to the `pit38 import` subcommand group in
   `pit38/cli.py`.
6. Write unit tests for the row parser and at least one E2E test with
   an **anonymized** sample CSV under `tests/e2e/fixtures/`. Remove
   account numbers, names, and PII before committing.
7. Update the "Supported Brokers" table in both `README.md` and
   `README.pl.md`.

If you're unsure whether a format quirk belongs in shared normalization
or plugin-local code, open a draft PR — easier to discuss over real code
than in the abstract.

**Before you start coding**, please open a broker-support issue using
the [broker support template](.github/ISSUE_TEMPLATE/broker_support_en.md)
and attach a sanitized CSV sample. This lets us confirm we have
reference data to validate against, and flags any format ambiguities
before you invest time.

## Reporting tax-law bugs

Bad tax math = wrong PIT filings, so tax-correctness bugs get special
treatment. If you suspect `pit38` produces the wrong number:

1. **Open an issue immediately** — don't wait until you have a fix.
   Other users may be affected.
2. **Include a minimal reproducible CSV** (anonymized — remove PII
   before pasting). Five rows is usually enough.
3. **Cite the tax rule.** If you can, point to the article of the
   ustawa (*Ustawa o podatku dochodowym od osób fizycznych*) or to
   [docs/TAX_RULES.md](docs/TAX_RULES.md) section that you believe is
   being violated. A KIS interpretation or forum link works too.
4. **State expected vs actual output.** "Expected tax of 123.45 PLN
   because X, got 678.90 PLN." Numbers matter here.
5. **Label it `tax-correctness`.** Maintainers will prioritize these
   above feature work.

If you fix a tax-law bug yourself, update `docs/TAX_RULES.md` /
`docs/TAX_RULES.pl.md` if the rule itself was under-documented, and
add a regression test with the reproducing fixture so it can't silently
come back.

## Code of Conduct

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).
By participating, you agree to abide by its terms. Issues relating to
conduct can be raised privately via a GitHub issue marked confidential
or by emailing the maintainer listed in `CODE_OF_CONDUCT.md`.

## Where to ask questions

- **[GitHub Discussions](https://github.com/pbialon/pit-38/discussions)**
  — tax-rule Q&A, broker format questions, general discussion. English
  and Polish both welcome.
- **[Issues](https://github.com/pbialon/pit-38/issues)** — bug reports,
  feature requests, broker-support requests. Templates exist for each.
- **PR comments** — implementation-level questions during review.

Happy hacking, and thanks for helping make Polish tax filing less
painful.
