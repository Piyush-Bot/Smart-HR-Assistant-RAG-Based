from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from retriever import retrieve_context
from llm import query_ollama
import re
import shutil
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
def ask_question(question: str):
    context = retrieve_context(question)

    prompt = f"""You are an assistant. Answer ONLY using the given context below. Do not use outside knowledge.

If the answer is not clearly stated in the context, reply with: "Not found in the provided context."

{context}

Question: {question}

Answer:"""

    answer = query_ollama(prompt)
    answer = answer.strip()
    if answer.startswith("Answer:"):
        answer = answer[len("Answer:"):].strip()
    # Remove trailing duplicate "Answer: X" (e.g. "...November 2000. Answer: November 2000")
    answer = re.sub(r"[.\s]+Answer:\s+.*$", "", answer, flags=re.IGNORECASE).strip()
    return {"answer": answer}


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = f"../data/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "File uploaded successfully"}