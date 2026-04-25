<!-- PR discussions welcome in English or Polish — whichever you're more
     comfortable with. The template is in English as most contributors
     are developer-focused, but reviewers will reply in your language. -->

## Summary

<!-- 1-3 sentences: what does this PR do, and why? -->

Closes #

## Changes

<!-- Bullet list of notable changes. Group by module if helpful. -->

-

## Tax-correctness impact

<!-- Does this change affect tax calculations? -->

- [ ] **No impact** — purely refactor, docs, tests, CI
- [ ] **Yes, tax output changes** — explain what and why, and whether
      existing test expectations were updated

<!-- If yes, describe the delta:
     - Which inputs produce different output now?
     - Is the new output correct per the ustawa? Cite article.
     - Did you update reference fixtures / expected values? -->

## Testing

- [ ] `pytest tests/` passes locally
- [ ] Added tests for new behaviour (or explained why not applicable)
- [ ] Tested on a real CSV if tax-calc change

<!-- How did you verify the change end-to-end? Manual smoke test? -->

## Documentation

- [ ] Updated `TAX_RULES.md` / `TAX_RULES.pl.md` if tax rules clarified or corrected
- [ ] Updated `CHANGELOG.md` with an entry
- [ ] Updated relevant README / plugin docs
- [ ] Updated `TAX_LAW_AUDIT.md` if this closes an audit issue

## Reviewer notes

<!-- Anything the reviewer should know? Gotchas, deferred work, rationale
     for a non-obvious choice, links to related issues / prior discussion. -->
