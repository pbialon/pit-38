# GitHub Discussions setup

This document captures the category layout and seed threads created for
pit-38 Discussions. Future maintainers can use it to reconstitute the
space if needed, or to understand the rationale behind the category split.

## Categories

| Category | Format | Purpose |
|----------|--------|---------|
| **Announcements** 📣 | Announcement (maintainer-only) | Release notes, tax-law updates, breaking changes |
| **Q&A** 🙏 | Question + marked answer | Tax-rule interpretation questions where there's a definite answer |
| **Broker support** 🏦 | Open-ended | Broker requests, sanitized CSV samples, discussion of quirks |

Other default categories (General, Ideas, Polls, Show and tell) are
hidden — we want a focused, low-cognitive-load surface. If traffic grows,
re-enabling them is trivial in Settings → Discussions.

## Seed threads

| # | Category | Title |
|---|----------|-------|
| [#72](https://github.com/pbialon/pit-38/discussions/72) | Q&A | How do I handle W-8BEN dividends in PIT-38? |
| [#73](https://github.com/pbialon/pit-38/discussions/73) | Broker support | Which broker should we support next? |
| [#74](https://github.com/pbialon/pit-38/discussions/74) | Announcements | Welcome to pit-38 Discussions |

## Posting conventions

- **Language**: Polish and English both welcome. Maintainers respond in
  the language of the thread. Use `[PL]` prefix in title if Polish-only.
- **Announcements**: maintainer-only by category configuration.
- **Broker support**: encourage sanitized CSV snippets (5–10 rows max,
  PII removed) rather than full exports. See issue #33 for an example
  of how real exports informed the BOM/locale fixes.
- **Q&A**: maintainers can mark the accepted answer to boost future
  searchability — we're using Discussions partly as a knowledge base.

## Links

- [Discussions landing](https://github.com/pbialon/pit-38/discussions)
- [Closing issue](https://github.com/pbialon/pit-38/issues/48)
