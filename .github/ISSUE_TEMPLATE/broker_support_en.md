---
name: "\U0001F1EC\U0001F1E7 Broker support request"
about: Request support for a new broker, or report a broker's CSV format change
title: "[BROKER] "
labels: ["broker-support", "help wanted"]
---

<!-- Use this when:
     - Your broker isn't in the supported list and you'd like it added
     - An existing broker changed their CSV format and pit-38 now breaks
     For general discussion first, try Discussions → Broker support. -->

## Broker

- **Name**:
- **Region** (US / EU / PL / other):
- **Asset class** (stocks / crypto / both):
- **Website** (helpful for sample format docs):

## Sanitized export sample

<!-- ⚠️ IMPORTANT: remove all PII first — account numbers, names, etc.
     Paste 5-10 rows that cover the typical operation types your broker
     emits. If the file is wide, a gist link is fine. -->

```csv
paste sanitized CSV here
```

## Typical columns

<!-- Copy the CSV header row verbatim. This is what pit-38 needs to parse. -->

## Operation types observed

<!-- List the distinct values in the "Type" or "Operation" column. Examples:
     Revolut uses "BUY - MARKET", "SELL - LIMIT", "DIVIDEND", "CUSTODY FEE",
     "STOCK SPLIT", "CASH WITHDRAWAL", etc. -->

## Known quirks

<!-- Anything non-standard? Examples:
     - Non-UTF-8 encoding or BOM
     - European number format (1.234,56) or space as thousand separator
     - Minus sign placement (USD -0.07 vs -USD 0.07)
     - Localized column names (PL/DE/etc.)
     - Multiple sheets (Excel export) -->

## Tax year coverage

<!-- Which tax years does your sample span? Older formats may differ. -->

## Can you help implement?

- [ ] I'd like to contribute the plugin myself (plugin dev docs coming — see #49, #50)
- [ ] I can provide test data but not code
- [ ] Just a request

## Additional context

<!-- Links to broker's API docs, related issues, previous GitHub projects
     for this broker, etc. -->
