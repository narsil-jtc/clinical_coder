"""Retrieval helpers over normalized terminology data."""

from __future__ import annotations

import logging
import os

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from clinical_coder.config import settings
from clinical_coder.terminology.index_store import build_document, terminology_collection_name
from clinical_coder.terminology.repository import load_terminology_bundle

logger = logging.getLogger(__name__)

N_RESULTS = 5


def _keyword_score(query: str, title: str) -> float:
    q_tokens = {token for token in query.lower().split() if token}
    t_tokens = {token for token in title.lower().split() if token}
    if not q_tokens or not t_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


def keyword_retrieve(query_terms: list[str], path_override: str | None = None, n_results: int = N_RESULTS) -> list[dict]:
    """Cheap local fallback retrieval using token overlap."""

    bundle = load_terminology_bundle(path_override)
    results: list[dict] = []
    seen_codes: set[str] = set()

    for term in query_terms:
        scored = sorted(
            (
                (
                    _keyword_score(term, record.title),
                    record,
                )
                for record in bundle.records
                if record.billable
            ),
            key=lambda item: item[0],
            reverse=True,
        )[:n_results]
        for score, record in scored:
            if score <= 0 or record.code in seen_codes:
                continue
            seen_codes.add(record.code)
            results.append(
                {
                    "code": record.code,
                    "description": record.title,
                    "relevance_score": round(score, 4),
                    "source_entity": term,
                    "source_id": record.source_id,
                    "edition": record.edition,
                    "notes": record.notes,
                }
            )
    results.sort(key=lambda item: item["relevance_score"], reverse=True)
    return results


def chroma_retrieve(
    query_terms: list[str],
    path_override: str | None = None,
    n_results: int = N_RESULTS,
) -> list[dict]:
    """Vector retrieval against the local Chroma index."""

    import chromadb
    from chromadb.config import Settings as ChromaSettings
    from sentence_transformers import SentenceTransformer

    if not query_terms:
        return []

    bundle = load_terminology_bundle(path_override)
    collection_name = terminology_collection_name(bundle.source_id, bundle.edition)

    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
    if collection.count() == 0:
        return []

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(query_terms, show_progress_bar=False)
    if hasattr(embeddings, "tolist"):
        embeddings = embeddings.tolist()
    query_result = collection.query(query_embeddings=embeddings, n_results=n_results)

    seen_codes: set[str] = set()
    results: list[dict] = []
    for index, term in enumerate(query_terms):
        for code_id, document, metadata, distance in zip(
            query_result["ids"][index],
            query_result["documents"][index],
            query_result["metadatas"][index],
            query_result["distances"][index],
        ):
            if code_id in seen_codes:
                continue
            if metadata.get("source_id") != bundle.source_id or metadata.get("edition") != bundle.edition:
                continue
            seen_codes.add(code_id)
            results.append(
                {
                    "code": metadata.get("code", code_id),
                    "description": metadata.get("description", document),
                    "relevance_score": round(1.0 - distance, 4),
                    "source_entity": term,
                    "source_id": metadata.get("source_id", ""),
                    "edition": metadata.get("edition", ""),
                    "notes": metadata.get("notes", ""),
                }
            )
    results.sort(key=lambda item: item["relevance_score"], reverse=True)
    return results


def retrieve_context(query_terms: list[str], path_override: str | None = None) -> list[dict]:
    """Use Chroma when available and populated, otherwise fall back to local keyword retrieval."""

    try:
        results = chroma_retrieve(query_terms, path_override=path_override)
        if results:
            return results
    except Exception as exc:
        logger.warning("Vector retrieval unavailable, falling back to keyword retrieval: %s", exc)
    return keyword_retrieve(query_terms, path_override=path_override)
