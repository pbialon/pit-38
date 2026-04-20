# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [CalVer](https://calver.org/) (`YYYY.M.DD`).

## [2026.4.20] — 2026-04-20

### Added
- `pyproject.toml` — proper Python packaging, installable via `pipx install .`
- `pit38` CLI entry point with subcommands: `stock`, `crypto`, `import`
- `pit38 import` subcommand for broker imports (`revolut-stock`, `revolut-crypto`, `etrade`, `binance`)
- `README.pl.md` — Polish version of README, linked from main README
- `TAX_LAW_AUDIT.md` — tax law compliance analysis against Polish PIT regulations
- `TEST_GAPS.md` — documented missing test coverage
- `CLAUDE.md` — project context for Claude Code
- Missing README for Revolut stock plugin
- CalVer versioning convention

### Changed
- Renamed `src/` to `pit38/` (proper Python package)
- All imports updated to `pit38.*` prefix
- `README.md` rewritten — cleaner structure, supported brokers table, disclaimer
- CI workflow uses `pip install -e ".[dev]"` + `pytest` instead of `PYTHONPATH` hack

### Removed
- `requirements.txt` (replaced by `pyproject.toml` dependencies)
- `PYTHONPATH=./src` requirement
- Dead `test_profit_calculator` function (broken since stock plugin refactor)

## [0.x] — Pre-release history

### Stock support
- Revolut stock plugin with BUY/SELL, dividends, custody fees, stock splits
- E*Trade stock plugin
- FIFO profit calculation per stock
- Stock split handling (quantity adjustment)
- Service fee tracking as deductible cost

### Crypto support
- Revolut crypto plugin
- Binance crypto plugin
- Yearly cost/income aggregation for crypto

### Core
- NBP exchange rate integration (table A, day-before rule)
- Polish holidays calendar for business day calculation
- 19% flat tax calculation with loss carry-forward
- Multi-source CSV loader (combine files from different brokers)
- CSV validator for standardized format
