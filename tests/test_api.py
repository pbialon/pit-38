import json
from datetime import date
from decimal import Decimal

import pytest

from pit38.api import (
    DateRange,
    FormField,
    ImportResult,
    InputDocument,
    Issue,
    ReadinessResult,
    RowDecision,
    SourceRef,
)


def test_import_result_serializes_source_metadata_and_stable_issue_code():
    document = InputDocument("A", b"kind\nsynthetic\n", 2026, "account-A")
    reference = SourceRef(document.document_id, 2)
    issue = Issue(
        code="MISSING_BUY",
        severity="error",
        next="add_earlier_statement",
        source=reference,
    )
    result = ImportResult(
        document_id=document.document_id,
        variant="synthetic",
        date_ranges=(DateRange(date(2026, 1, 2), date(2026, 1, 3), "observed_rows"),),
        rows=(RowDecision(2, "event", "SELL", "event-A"),),
        issues=(issue,),
    )

    payload = json.loads(json.dumps(result.to_dict()))

    assert payload == {
        "schema_version": 1,
        "document_id": "A",
        "variant": "synthetic",
        "date_ranges": [
            {"start": "2026-01-02", "end": "2026-01-03", "origin": "observed_rows"}
        ],
        "rows": [
            {"row": 2, "classification": "event", "reason": "SELL", "event_id": "event-A"}
        ],
        "issues": [
            {
                "code": "MISSING_BUY",
                "severity": "error",
                "next": "add_earlier_statement",
                "source": {"document": "A", "row": 2},
                "related_sources": [],
            }
        ],
    }


@pytest.mark.parametrize(("amount", "expected"), [("620.00", "620.00"), ("1E-8", "0.00000001")])
def test_ready_result_serializes_amount_as_decimal_text(amount, expected):
    result = ReadinessResult(
        2026, "ready", form_fields=(FormField("synthetic-field", Decimal(amount)),)
    )

    assert json.loads(json.dumps(result.to_dict())) == {
        "schema_version": 1,
        "tax_year": 2026,
        "status": "ready",
        "issues": [],
        "form_fields": [{"field_id": "synthetic-field", "amount": expected}],
    }


def test_blocked_result_serializes_no_form_fields():
    issue = Issue(code="MISSING_BUY", severity="error")
    result = ReadinessResult(2026, "blocked", issues=(issue,))

    payload = json.loads(json.dumps(result.to_dict()))

    assert payload["status"] == "blocked"
    assert payload["issues"][0]["code"] == "MISSING_BUY"
    assert payload["form_fields"] == []
    with pytest.raises(ValueError, match="blocked result"):
        ReadinessResult(
            2026, "blocked", form_fields=(FormField("synthetic-field", Decimal("1")),)
        )
