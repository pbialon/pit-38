"""Extract plain text from an IBI Capital order confirmation PDF.

Thin wrapper over pdfplumber so callers don't need to know about the
``with`` protocol or per-page iteration. The parser module sits directly
on top of this and treats the full-document text as a flat string.
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber


def extract_text(pdf_path: str | Path) -> str:
    """Return the concatenated text of every page in ``pdf_path``.

    pdfplumber preserves layout order reasonably well for IBI's fixed
    template, which is all the parser needs. Multi-page orders still
    work because pages join with newlines and the parser uses global
    regex search.
    """
    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)
