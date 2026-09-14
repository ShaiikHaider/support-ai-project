"""
RAG knowledge base backed by ChromaDB (drop-in swappable for FAISS/Pinecone —
see get_embedding_function for the seam).

Retrieval results are always returned as explicitly labeled "retrieved
information" objects, never merged silently into a final answer, per the
system's information-retrieval-vs-action separation requirement.
"""
from dataclasses import dataclass

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings
from app.kb.seed_documents import KB_DOCUMENTS

_client: chromadb.ClientAPI | None = None
_collection = None


@dataclass
class RetrievedChunk:
    id: str
    title: str
    category: str
    content: str
    relevance_score: float


def _get_embedding_function():
    """Uses OpenAI embeddings when a key is configured; otherwise falls back
    to Chroma's local default (sentence-transformers) so the system still
    runs end-to-end without external credentials during development."""
    if settings.OPENAI_API_KEY:
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_EMBEDDING_MODEL,
        )
    return embedding_functions.DefaultEmbeddingFunction()


def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    _collection = _client.get_or_create_collection(
        name=settings.KB_COLLECTION_NAME,
        embedding_function=_get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )

    if _collection.count() == 0:
        _seed_collection(_collection)

    return _collection


def _seed_collection(collection) -> None:
    collection.add(
        ids=[doc["id"] for doc in KB_DOCUMENTS],
        documents=[doc["content"] for doc in KB_DOCUMENTS],
        metadatas=[{"title": doc["title"], "category": doc["category"]} for doc in KB_DOCUMENTS],
    )


def retrieve(query: str, category_hint: str | None = None, top_k: int = 4) -> list[RetrievedChunk]:
    """Search FAQs / product docs / policies. If a category hint (from the
    Triage Agent's classification) is available, results are filtered to it
    first, then broadened if too few matches are found."""
    collection = get_collection()

    where = {"category": category_hint} if category_hint else None
    result = collection.query(query_texts=[query], n_results=top_k, where=where)

    chunks = _parse_result(result)

    if len(chunks) < 2 and where is not None:
        # broaden search across the full KB if the category filter was too narrow
        result = collection.query(query_texts=[query], n_results=top_k)
        chunks = _parse_result(result)

    return chunks


def _parse_result(result) -> list[RetrievedChunk]:
    chunks: list[RetrievedChunk] = []
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0] if result.get("distances") else [None] * len(ids)

    for i, doc_id in enumerate(ids):
        distance = dists[i]
        score = round(1 - distance, 4) if distance is not None else 0.0
        chunks.append(
            RetrievedChunk(
                id=doc_id,
                title=metas[i].get("title", ""),
                category=metas[i].get("category", ""),
                content=docs[i],
                relevance_score=score,
            )
        )
    return chunks
