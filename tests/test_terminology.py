from pathlib import Path

from clinical_coder.ingestion.uk_claml import load_uk_claml_bundle
from clinical_coder.ingestion.who_claml import load_who_claml_bundle


FIXTURE = Path(__file__).parent / "fixtures" / "sample_claml.xml"


def test_who_claml_ingestion_parses_records():
    bundle = load_who_claml_bundle(FIXTURE)
    assert bundle.records
    codes = {record.code: record for record in bundle.records}
    assert "I21.0" in codes
    assert codes["I21.0"].billable is True
    assert "Anterior STEMI" in codes["I21.0"].notes


def test_uk_adapter_uses_same_normalized_shape():
    bundle = load_uk_claml_bundle(FIXTURE)
    assert bundle.source_id == "uk_icd10_5e"
    assert any(record.code == "E11.2" for record in bundle.records)
