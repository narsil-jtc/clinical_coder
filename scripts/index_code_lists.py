"""Build the local Chroma terminology index from the active XML terminology source."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from chromadb.config import Settings as ChromaSettings

from clinical_coder.config import settings
from clinical_coder.terminology.index_store import build_document, terminology_collection_name
from clinical_coder.terminology.repository import load_terminology_bundle


def main() -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    bundle = load_terminology_bundle(settings.icd10_code_list_path)
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    collection_name = terminology_collection_name(bundle.source_id, bundle.edition)
    collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
    if collection.count():
        client.delete_collection(collection_name)
        collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    model = SentenceTransformer("all-MiniLM-L6-v2")
    billable_records = [record for record in bundle.records if record.billable]

    batch_size = 256
    for start in range(0, len(billable_records), batch_size):
        batch = billable_records[start : start + batch_size]
        documents = [build_document(record) for record in batch]
        ids = [record.code for record in batch]
        embeddings = model.encode(documents, show_progress_bar=False).tolist()
        metadatas = [
            {
                "code": record.code,
                "description": record.title,
                "source_id": record.source_id,
                "edition": record.edition,
                "notes": " | ".join(record.notes[:3]),
            }
            for record in batch
        ]
        collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    print(f"Indexed {len(billable_records)} billable records from {Path(settings.icd10_code_list_path).name}")
    print(f"Chroma collection: {collection_name}")
    print(f"Chroma collection count: {collection.count()}")


if __name__ == "__main__":
    main()
