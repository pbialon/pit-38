"""Shared CSV reading utilities.

Centralizes two quirks that broke real-world broker exports (#33):

1. UTF-8 BOM — Revolut (and many Excel-generated CSVs) prefix files with
   `\xef\xbb\xbf`. Opening with plain `"r"` leaves the BOM in the first
   column name (e.g. `'\\ufeffdate'` instead of `'date'`). `utf-8-sig`
   strips it cleanly and is a no-op for files without BOM.

2. Header case drift — brokers change column capitalization between
   exports (`Date` → `date`). We normalize headers to `lower().strip()`
   once at read time so downstream code uses a stable form.

Write side stays as plain `utf-8` (no BOM) — Postel's law: liberal in
what we accept, strict in what we emit.
"""
import csv
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def open_csv_reader(path: str, delimiter: str = ",") -> Iterator[csv.DictReader]:
    """Open CSV tolerantly: strips UTF-8 BOM and normalizes headers.

    Usage:
        with open_csv_reader("export.csv") as reader:
            for row in reader:
                value = row["date"]  # always lowercase
    """
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames:
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        yield reader
