"""
Pydantic models for code suggestions, validation flags, and human review decisions.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class CodeSystem(StrEnum):
    ICD10 = "ICD-10"
    OPCS4 = "OPCS-4"
    SNOMED = "SNOMED-CT"


class ValidationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ReviewDecision(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"
    PENDING = "pending"


class CodeCandidate(BaseModel):
    """A single candidate code suggested by the LLM."""

    code: str = Field(description="The WHO ICD-10 code string, e.g. 'I21.0'")
    description: str = Field(description="Official WHO ICD-10 description")
    code_system: CodeSystem = Field(default=CodeSystem.ICD10)
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence 0-1")
    supporting_entity: str = Field(description="Entity term this code addresses")
    evidence_span: str = Field(description="Exact text from note supporting this code")
    coding_rationale: str = Field(description="Why this specific code, not a parent")
    alternative_codes: list[str] = Field(default_factory=list)
    requires_additional_code: bool = False
    suggested_additional_codes: list[str] = Field(default_factory=list)


class CodingResult(BaseModel):
    """Structured output from the code suggestion LLM call."""

    code_candidates: list[CodeCandidate] = Field(default_factory=list)
    missing_specificity_flags: list[dict] = Field(default_factory=list)


class ValidationFlag(BaseModel):
    """A single rule-based validation finding."""

    code: str
    rule_id: str
    severity: ValidationSeverity
    message: str
    suggested_action: str


class CodeExplanation(BaseModel):
    """Natural-language explanation for one code candidate."""

    code: str
    plain_english: str = Field(description="<= 60 word explanation for the reviewer")
    key_documentation: str = Field(description="The specific text that drives this code")
    why_not_alternatives: str = Field(description="Why alternatives were not selected")


class ExplanationResult(BaseModel):
    """Structured output from the explanation LLM call."""

    explanations: list[CodeExplanation] = Field(default_factory=list)


class ReviewedCode(BaseModel):
    """A code candidate after human review."""

    candidate: CodeCandidate
    explanation: CodeExplanation | None = None
    validation_flags: list[ValidationFlag] = Field(default_factory=list)
    decision: ReviewDecision = ReviewDecision.PENDING
    modified_code: str | None = None
    reviewer_note: str = ""
