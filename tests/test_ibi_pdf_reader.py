"""Tests for the pdfplumber wrapper.

The wrapper is three lines of real logic. The tests below cover both
branches: the ImportError guard (for users who install ``pit-38``
without the ``[ibi]`` extra) and the happy path, exercised against a
minimal hand-crafted PDF so we don't need to commit a binary fixture
that would risk leaking PII.
"""
import builtins
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

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


class TestExtractTextImportGuard(TestCase):
    def test_import_error_has_actionable_message(self):
        # Simulate a user who ran `pipx install pit-38` without `[ibi]`
        # by hiding any already-imported pdfplumber module and blocking
        # re-import.
        real_import = builtins.__import__

        def _block_pdfplumber(name, *args, **kwargs):
            if name == "pdfplumber":
                raise ImportError("No module named 'pdfplumber'")
            return real_import(name, *args, **kwargs)

        saved_pdfplumber = sys.modules.pop("pdfplumber", None)
        try:
            with patch.object(builtins, "__import__", _block_pdfplumber):
                from pit38.plugins.stock.ibi_capital import pdf_reader

                with self.assertRaises(ImportError) as ctx:
                    pdf_reader.extract_text("/tmp/whatever.pdf")

            msg = str(ctx.exception)
            self.assertIn("pdfplumber", msg)
            # The whole point of the wrapped error is steering the user
            # to the right install incantation.
            self.assertIn("pit-38[ibi]", msg)
        finally:
            if saved_pdfplumber is not None:
                sys.modules["pdfplumber"] = saved_pdfplumber


class TestExtractTextHappyPath(TestCase):
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
