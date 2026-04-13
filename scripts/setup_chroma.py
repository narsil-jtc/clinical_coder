"""Initialise local Chroma collections used by the prototype."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from chromadb.config import Settings as ChromaSettings

from clinical_coder.config import settings
from clinical_coder.terminology.index_store import terminology_collection_name
from clinical_coder.terminology.repository import load_terminology_bundle


def main() -> None:
    import chromadb

    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    bundle = load_terminology_bundle(settings.icd10_code_list_path)
    terminology_collection = terminology_collection_name(bundle.source_id, bundle.edition)
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    for name in [terminology_collection, "coding_rules", "worked_examples"]:
        collection = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        print(f"Collection '{name}': {collection.count()} documents")


if __name__ == "__main__":
    main()
