import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client(
    Settings(
        persist_directory="../db",
        is_persistent=True,
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection("hr_policies")


def retrieve_context(query, k=3):
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    return "\n\n".join(results["documents"][0])