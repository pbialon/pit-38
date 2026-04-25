---
name: "\U0001F1EC\U0001F1E7 Bug report"
about: Report incorrect tax calculations or tool crashes
title: "[BUG] "
labels: ["bug"]
---

<!-- Thanks for taking the time to report a bug! Please fill out the sections
     below — incomplete reports are harder to fix. For tax-rule questions
     (not code bugs), please use Discussions → Q&A instead. -->

## Environment

- **pit-38 version** (run `pip show pit-38 | grep Version`):
- **Python version**:
- **Operating system**:
- **Broker(s) involved**:
- **Tax year being calculated**:

## What happened

<!-- Describe the issue in 1-3 sentences. If the tax output is wrong,
     state expected vs actual; if the tool crashed, paste the traceback. -->

## Minimal CSV to reproduce

<!-- ⚠️ IMPORTANT: sanitize the file first.
     - Remove account numbers, SSN-like IDs, personal details
     - Keep only 5-10 transactions that trigger the bug
     - Do NOT paste full real broker exports -->

```csv
paste sanitized CSV here
```

## Expected tax output

<!-- What values should appear in the CLI output? Cite the ustawa article
     if the expected value follows from a specific rule (e.g. "art. 22 ust. 16
     says cost carry-forward is unlimited, so I expect X PLN deductible loss
     from 2022"). -->

## Actual tax output or error

<!-- Paste the full CLI output or the Python traceback. If possible, run
     with `--log-level DEBUG` for more context. -->

```
paste output here
```

## Additional context

<!-- Anything else? Related issues, what you've already tried, etc. -->
