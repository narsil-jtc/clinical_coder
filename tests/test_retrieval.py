from pathlib import Path

from clinical_coder.retrieval.terminology_retriever import chroma_retrieve, keyword_retrieve
from clinical_coder.terminology.repository import load_terminology_bundle


FIXTURE = Path(__file__).parent / "fixtures" / "sample_claml.xml"


def test_keyword_retrieval_returns_matching_codes():
    results = keyword_retrieve(["anterior myocardial infarction"], path_override=str(FIXTURE), n_results=3)
    assert results
    assert results[0]["code"] == "I21.0"


def test_chroma_retrieval_uses_source_scoped_collection(monkeypatch):
    bundle = load_terminology_bundle(str(FIXTURE))

    class FakeCollection:
        def count(self):
            return 1

        def query(self, query_embeddings, n_results):
            return {
                "ids": [["I21.0", "X99.99"]],
                "documents": [["Acute transmural myocardial infarction", "Wrong-standard code"]],
                "metadatas": [[
                    {
                        "code": "I21.0",
                        "description": "Acute transmural myocardial infarction of anterior wall",
                        "source_id": bundle.source_id,
                        "edition": bundle.edition,
                        "notes": "",
                    },
                    {
                        "code": "X99.99",
                        "description": "Mismatched terminology entry that should be filtered out",
                        "source_id": "other_source",
                        "edition": "Other edition",
                        "notes": "",
                    },
                ]],
                "distances": [[0.1, 0.01]],
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_or_create_collection(self, name, metadata):
            return FakeCollection()

    class FakeModel:
        def __init__(self, *args, **kwargs):
            pass

        def encode(self, query_terms, show_progress_bar=False):
            return [[0.0, 0.1, 0.2] for _ in query_terms]

    import sys
    import types

    fake_chromadb = types.SimpleNamespace(PersistentClient=FakeClient)
    fake_chromadb_config = types.SimpleNamespace(Settings=lambda anonymized_telemetry=False: None)
    fake_sentence_transformers = types.SimpleNamespace(SentenceTransformer=FakeModel)

    monkeypatch.setitem(sys.modules, "chromadb", fake_chromadb)
    monkeypatch.setitem(sys.modules, "chromadb.config", fake_chromadb_config)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_sentence_transformers)

    results = chroma_retrieve(["anterior myocardial infarction"], path_override=str(FIXTURE), n_results=2)
    assert [item["code"] for item in results] == ["I21.0"]
