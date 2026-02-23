from retriever import retrieve_context
from llm import query_ollama

def ask_hr_bot(question):
    context = retrieve_context(question)

    prompt = f"""
You are an HR assistant chatbot.
Answer only using the context provided below.
If the answer is not found in the context, say:
"Not found in HR policy."

Context:
{context}

Question:
{question}
"""

    return query_ollama(prompt)


if __name__ == "__main__":
    while True:
        q = input("\nAsk HR: ")
        answer = ask_hr_bot(q)
        print("\nAnswer:\n", answer)