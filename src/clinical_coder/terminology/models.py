"""Canonical terminology models used across ingestion, retrieval, and rules."""

from pydantic import BaseModel, Field


class TerminologyRecord(BaseModel):
    """Normalized representation of one terminology code entry."""

    source_id: str
    edition: str
    code: str
    title: str
    hierarchy: list[str] = Field(default_factory=list)
    chapter: str | None = None
    billable: bool = True
    is_leaf: bool = True
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class TerminologyBundle(BaseModel):
    """Collection of normalized terminology records from a single source."""

    source_id: str
    edition: str
    records: list[TerminologyRecord] = Field(default_factory=list)
