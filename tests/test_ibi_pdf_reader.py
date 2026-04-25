"""Tests for the pdfplumber wrapper.

The wrapper is three lines of real logic. We exercise it against a
minimal hand-crafted PDF so we don't need to commit a binary fixture
that would risk leaking PII from real IBI statements.
"""
import tempfile
from pathlib import Path
from unittest import TestCase

# A valid but minimal PDF containing a single page with one text run.
# Hand-crafted so we can test without committing a binary fixture —
# anonymization of real IBI PDFs would be involved, and pdfplumber
# itself doesn't ship sample PDFs. Offsets in the xref table are
# manually aligned with the object declarations above them.
_MINIMAL_PDF_BYTES = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 50>>stream
BT /F1 12 Tf 72 720 Td (IBI fixture text) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000054 00000 n
0000000101 00000 n
0000000200 00000 n
0000000290 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
352
%%EOF
"""


class TestExtractText(TestCase):
    def test_extracts_text_from_minimal_pdf(self):
        from pit38.plugins.stock.ibi_capital.pdf_reader import extract_text

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(_MINIMAL_PDF_BYTES)
            path = Path(f.name)

        try:
            text = extract_text(path)
            self.assertIn("IBI fixture text", text)
        finally:
            path.unlink()

    def test_accepts_string_path(self):
        # pdfplumber.open accepts both str and Path; the wrapper signature
        # is typed as str | Path so we test both.
        from pit38.plugins.stock.ibi_capital.pdf_reader import extract_text

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(_MINIMAL_PDF_BYTES)
            path_str = f.name

        try:
            text = extract_text(path_str)
            self.assertIn("IBI fixture text", text)
        finally:
            Path(path_str).unlink()
