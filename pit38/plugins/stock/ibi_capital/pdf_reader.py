"""Extract plain text from an IBI Capital order confirmation PDF.

Thin wrapper over pdfplumber so the optional ``[ibi]`` dependency stays
isolated. Plugin users who don't need IBI support don't install
pdfplumber and don't get import-time breakage.
"""
from __future__ import annotations

from pathlib import Path


def extract_text(pdf_path: str | Path) -> str:
    """Return the concatenated text of every page in ``pdf_path``.

    pdfplumber preserves layout order reasonably well for IBI's fixed
    template, which is all the parser needs. Rare multi-page orders
    still work because we join pages with newlines and the parser uses
    global regex search.
    """
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError(
            "IBI Capital plugin requires pdfplumber. "
            "Install with: pip install 'pit-38[ibi]'"
        ) from e

    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)
