"""ClaML XML ingestion shared by WHO and UK ICD adapters."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from clinical_coder.terminology.models import TerminologyBundle, TerminologyRecord


def load_claml_bundle(path: str | Path, source_id: str, edition: str) -> TerminologyBundle:
    """Parse a ClaML file into normalized terminology records."""

    result: list[TerminologyRecord] = []
    path = Path(path)

    current_code: str | None = None
    current_kind: str | None = None
    current_description: str | None = None
    current_has_subclass = False
    current_notes: list[str] = []
    current_metadata: dict[str, str] = {}
    current_hierarchy: list[str] = []
    preferred_rubric_kind: str | None = None
    in_label = False

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = elem.tag

        if event == "start":
            if tag == "Class":
                current_code = elem.get("code")
                current_kind = elem.get("kind")
                current_description = None
                current_has_subclass = False
                current_notes = []
                current_metadata = {}
                usage = elem.get("usage")
                if usage:
                    current_metadata["usage"] = usage

            elif tag == "SubClass" and current_code:
                current_has_subclass = True
                child_code = elem.get("code")
                if child_code:
                    current_hierarchy = [current_code, child_code]

            elif tag == "Rubric":
                preferred_rubric_kind = elem.get("kind")

            elif tag == "Label":
                in_label = True

        else:
            if tag == "Label" and in_label and current_code:
                text = " ".join(part.strip() for part in elem.itertext() if part.strip())
                if text:
                    if preferred_rubric_kind == "preferred" and current_description is None:
                        current_description = text
                    elif preferred_rubric_kind in {"inclusion", "exclusion", "coding-hint", "note"}:
                        current_notes.append(text)
                in_label = False

            elif tag == "Rubric":
                preferred_rubric_kind = None

            elif tag == "Class":
                if current_code and current_description:
                    result.append(
                        TerminologyRecord(
                            source_id=source_id,
                            edition=edition,
                            code=current_code,
                            title=current_description,
                            hierarchy=current_hierarchy[:-1] if current_hierarchy else [],
                            billable=not current_has_subclass and current_kind == "category",
                            is_leaf=not current_has_subclass,
                            notes=current_notes,
                            metadata=current_metadata,
                        )
                    )
                elem.clear()
                current_code = None
                current_kind = None
                current_description = None
                current_has_subclass = False
                current_notes = []
                current_metadata = {}
                current_hierarchy = []

    return TerminologyBundle(source_id=source_id, edition=edition, records=result)
