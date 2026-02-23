import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

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


def chunk_text(text, chunk_size=500):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def ingest_documents():
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

        for i, chunk in enumerate(chunks):
            embedding = embedding_model.encode(chunk).tolist()

            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{file}_{i}"]
            )

        print(f"✅ Ingested: {file}")

    print("🎉 All documents ingested successfully.")


if __name__ == "__main__":
    ingest_documents()