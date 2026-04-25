"""Resolve the ``Company`` field of an IBI order PDF to a stock ticker.

IBI order reports don't include the NASDAQ/NYSE ticker — only a company
name such as ``monday.com``. The mapping to tickers lives in
``companies.json`` shipped alongside this module; seeding and extension
happen via PR. The ``--ticker`` CLI flag overrides the mapping so a user
whose company isn't in the JSON can still import without waiting for a
PR merge.

The JSON is loaded once per process and cached at module level. Lookup
is case-insensitive and trims surrounding whitespace, because we can't
guarantee IBI's formatting stays 100% stable across account types.
"""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Mapping


class UnknownCompanyError(KeyError):
    """Raised when ``Company`` from a PDF has no ticker mapping and no override."""


_COMPANIES_JSON = "companies.json"
_PR_LINK = (
    "https://github.com/pbialon/pit-38/blob/main/"
    "pit38/plugins/stock/ibi_capital/companies.json"
)


@lru_cache(maxsize=1)
def _load_mapping() -> Mapping[str, str]:
    raw = files(__package__).joinpath(_COMPANIES_JSON).read_text(encoding="utf-8")
    data = json.loads(raw)
    # Normalize keys to lowercase once up front so lookup stays O(1) and
    # doesn't allocate on each call.
    return {k.strip().lower(): v for k, v in data.items()}


def resolve_ticker(
    company: str,
    override: str | None = None,
    *,
    mapping: Mapping[str, str] | None = None,
) -> str:
    """Return the stock ticker for ``company``.

    ``override`` wins unconditionally — useful when the packaged JSON
    doesn't yet include the user's company, or when the PDF has an
    unusual company-name spelling.

    ``mapping`` is test-only dependency injection; production callers
    pass nothing and get the packaged ``companies.json``.
    """
    if override:
        return override

    table = mapping if mapping is not None else _load_mapping()
    key = company.strip().lower()
    if key not in table:
        raise UnknownCompanyError(
            f"Company '{company}' has no ticker mapping. "
            f"Either pass --ticker <SYMBOL> on the CLI, or open a PR "
            f"adding '{company}' to {_PR_LINK}"
        )
    return table[key]
