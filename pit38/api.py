"""Public data contracts for document import and PIT-38 readiness."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

__all__ = [
    "InputDocument",
    "SourceRef",
    "Issue",
    "DateRange",
    "RowDecision",
    "ImportResult",
    "FormField",
    "ReadinessResult",
]

_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class InputDocument:
    """A document supplied by the caller, with local pseudonymous identifiers."""

    document_id: str
    content: bytes
    tax_year: int
    account_alias: str
    declared_scope: str | None = None


@dataclass(frozen=True)
class SourceRef:
    document: str
    row: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {"document": self.document, "row": self.row}


@dataclass(frozen=True)
class Issue:
    code: str
    severity: Literal["error", "warning"]
    next: str | None = None
    source: SourceRef | None = None
    related_sources: tuple[SourceRef, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "next": self.next,
            "source": self.source.to_dict() if self.source else None,
            "related_sources": [source.to_dict() for source in self.related_sources],
        }


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date
    origin: Literal["document", "observed_rows", "caller"]

    def to_dict(self) -> dict[str, object]:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "origin": self.origin,
        }


@dataclass(frozen=True)
class RowDecision:
    row: int
    classification: Literal["event", "neutral", "unknown", "out_of_scope", "invalid"]
    reason: str
    event_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "row": self.row,
            "classification": self.classification,
            "reason": self.reason,
            "event_id": self.event_id,
        }


@dataclass(frozen=True)
class ImportResult:
    document_id: str
    variant: str | None = None
    date_ranges: tuple[DateRange, ...] = ()
    rows: tuple[RowDecision, ...] = ()
    issues: tuple[Issue, ...] = ()
    schema_version: int = field(default=_SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        rows = tuple(self.rows)
        if any(row.row < 1 for row in rows) or len({row.row for row in rows}) != len(rows):
            raise ValueError("Row decisions require distinct positive row numbers")
        object.__setattr__(self, "rows", rows)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "document_id": self.document_id,
            "variant": self.variant,
            "date_ranges": [period.to_dict() for period in self.date_ranges],
            "rows": [row.to_dict() for row in self.rows],
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class FormField:
    field_id: str
    amount: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("A form field amount must be a Decimal")
        if not self.amount.is_finite():
            raise ValueError("A form field amount must be finite")

    def to_dict(self) -> dict[str, str]:
        return {"field_id": self.field_id, "amount": format(self.amount, "f")}


@dataclass(frozen=True)
class ReadinessResult:
    tax_year: int
    status: Literal["blocked", "ready"]
    issues: tuple[Issue, ...] = ()
    form_fields: tuple[FormField, ...] = ()
    schema_version: int = field(default=_SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        issues = tuple(self.issues)
        form_fields = tuple(self.form_fields)
        if self.status == "blocked":
            if form_fields:
                raise ValueError("A blocked result cannot contain form fields")
        elif self.status == "ready":
            if not form_fields or any(issue.severity == "error" for issue in issues):
                raise ValueError("A ready result requires form fields and no errors")
        else:
            raise ValueError("Unknown readiness status")
        object.__setattr__(self, "issues", issues)
        object.__setattr__(self, "form_fields", form_fields)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "tax_year": self.tax_year,
            "status": self.status,
            "issues": [issue.to_dict() for issue in self.issues],
            "form_fields": [form_field.to_dict() for form_field in self.form_fields],
        }
