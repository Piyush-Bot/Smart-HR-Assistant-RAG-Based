import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# Load embedding model // all-mpnet-base-v2 =786 dimensions
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2") # 384 dimensions
embedding_model = SentenceTransformer("all-mpnet-base-v2") # 768 dimensions

# Persistent Chroma DB
client = chromadb.Client(
    Settings(
        persist_directory="../db",
        is_persistent=True,
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection("hr_policies")


def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text, first_chunk_size=500, chunk_size=600, overlap=150):
    """Fast chunking: one small first chunk (title block), then fixed-size sliding window."""
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= first_chunk_size:
        return [text]

    chunks = [text[:first_chunk_size]]
    start = first_chunk_size
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if end >= len(text):
            break
    return chunks


def ingest_documents():
    # Clear existing chunks so re-ingest uses new chunking (e.g. overlap) and metadata
    existing = collection.get(include=[])
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        print("Cleared existing collection for re-ingest.")

    files = os.listdir("../data")

    if not files:
        print("⚠ No files found in data folder.")
        return

    for file in files:
        file_path = f"../data/{file}"

        if file.endswith(".pdf"):
            text = load_pdf(file_path)

        elif file.endswith(".txt"):
            text = load_text(file_path)

        else:
            continue

        chunks = chunk_text(text)
        valid = [(i, c) for i, c in enumerate(chunks) if c and c.strip()]
        if not valid:
            print(f"⚠ No chunks for: {file}")
            continue

        indices, valid_chunks = zip(*valid)
        batch_size = 64  # encode in batches to avoid OOM
        all_embeddings = []
        for b in range(0, len(valid_chunks), batch_size):
            batch = valid_chunks[b : b + batch_size]
            all_embeddings.extend(embedding_model.encode(batch).tolist())
            print(f"  Encoding chunks {b + 1}-{min(b + batch_size, len(valid_chunks))}/{len(valid_chunks)} for {file}...", end="\r")
        print()  # newline after progress

        ids = [f"{file}_{i}" for i in indices]
        metadatas = [{"source": file, "chunk_index": i} for i in indices]
        collection.add(
            documents=list(valid_chunks),
            embeddings=all_embeddings,
            ids=ids,
            metadatas=metadatas,
        )
        print(f"✅ Ingested: {file} ({len(valid_chunks)} chunks)")

    print("\n🎉 All documents ingested successfully.")


if __name__ == "__main__":
    ingest_documents()