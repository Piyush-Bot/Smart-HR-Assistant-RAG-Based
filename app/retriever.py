import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-mpnet-base-v2")

client = chromadb.Client(
    Settings(
        persist_directory="../db",
        is_persistent=True,
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection("hr_policies")


def _get_first_chunks_per_document():
    """Get the first chunk of each document (title/author usually there). So 'title of the book' questions get the right context."""
    data = collection.get(include=["metadatas", "documents"])
    if not data["ids"]:
        return []
    by_source = {}
    for meta, doc in zip(data["metadatas"], data["documents"]):
        src = meta.get("source", "")
        idx = meta.get("chunk_index", 0)
        if src not in by_source or idx < by_source[src][0]:
            by_source[src] = (idx, doc)
    return [by_source[s][1] for s in sorted(by_source)]


def retrieve_context(query, k=7):
    """Retrieve top-k chunks. Always prepend the first chunk of each doc so title/author questions get the right context."""
    query_embedding = embedding_model.encode(query).tolist()

    # First chunks of each document (title page, author, etc.)
    first_chunks = _get_first_chunks_per_document()

    # Vector search for query-relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    vector_chunks = results["documents"][0] if results["documents"] else []

    # Prepend first chunks so "title of the book" / "author" are answered from title page; dedupe
    seen = set()
    ordered = []
    for c in first_chunks + vector_chunks:
        if c and c not in seen:
            seen.add(c)
            ordered.append(c)

    return "\n\n".join(ordered)