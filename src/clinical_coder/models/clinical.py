"""
Pydantic models for clinical note input and entity extraction output.
These are the data contracts between the parser, extractor, and downstream nodes.
"""
from enum import StrEnum
from pydantic import BaseModel, Field, field_validator


class EntityType(StrEnum):
    DIAGNOSIS = "diagnosis"
    PROCEDURE = "procedure"
    FINDING = "finding"
    MODIFIER = "modifier"


class Certainty(StrEnum):
    CONFIRMED = "confirmed"
    SUSPECTED = "suspected"
    HISTORICAL = "historical"
    RULED_OUT = "ruled_out"


class Laterality(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    BILATERAL = "bilateral"
    UNSPECIFIED = "unspecified"


class Severity(StrEnum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    UNSPECIFIED = "unspecified"


class Timing(StrEnum):
    ACUTE = "acute"
    CHRONIC = "chronic"
    SUBACUTE = "subacute"
    UNSPECIFIED = "unspecified"


class ClinicalEntity(BaseModel):
    """A single extracted clinical entity with all its modifiers."""

    term: str = Field(description="Exact clinical term as written in the note")
    normalized_term: str = Field(description="Standard medical term (e.g. 'myocardial infarction')")
    entity_type: EntityType = Field(description="Category of entity")
    certainty: Certainty = Field(default=Certainty.CONFIRMED)
    laterality: Laterality = Field(default=Laterality.UNSPECIFIED)
    severity: Severity = Field(default=Severity.UNSPECIFIED)
    timing: Timing = Field(default=Timing.UNSPECIFIED)
    text_span: str = Field(description="Exact quote from the note (≤ 100 chars)")

    @field_validator("entity_type", mode="before")
    @classmethod
    def coerce_entity_type(cls, v: str) -> str:
        """Map unrecognised entity types (e.g. 'medication') to 'finding'."""
        valid = {e.value for e in EntityType}
        return v if v in valid else "finding"

    @field_validator("certainty", mode="before")
    @classmethod
    def coerce_certainty(cls, v: str) -> str:
        valid = {e.value for e in Certainty}
        return v if v in valid else "confirmed"

    @field_validator("laterality", mode="before")
    @classmethod
    def coerce_laterality(cls, v: str) -> str:
        valid = {e.value for e in Laterality}
        return v if v in valid else "unspecified"

    @field_validator("severity", mode="before")
    @classmethod
    def coerce_severity(cls, v: str) -> str:
        valid = {e.value for e in Severity}
        return v if v in valid else "unspecified"

    @field_validator("timing", mode="before")
    @classmethod
    def coerce_timing(cls, v: str) -> str:
        valid = {e.value for e in Timing}
        return v if v in valid else "unspecified"


class ExtractionResult(BaseModel):
    """Structured output from the entity extraction LLM call."""

    entities: list[ClinicalEntity] = Field(default_factory=list)


class NoteSection(BaseModel):
    """A labelled section of a clinical note."""

    label: str = Field(description="Section name, e.g. 'assessment', 'history'")
    text: str = Field(description="Raw section text")
    char_start: int = Field(default=0)
    char_end: int = Field(default=0)


class ClinicalNote(BaseModel):
    """Top-level container for a clinical note submitted for coding."""

    note_id: str
    raw_text: str
    note_type: str = Field(default="discharge_summary")
    sections: list[NoteSection] = Field(default_factory=list)
