# import requests

# def query_ollama(prompt):
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "deepseek-r1",
#             "prompt": prompt,
#             "stream": False,
#             "options": {
#                 "temperature": 0.2,
#                 "top_k": 50
#             }
#         }
#     )

#     return response.json()["response"]
import requests

def query_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_k": 50
            }
        }
    )

    data = response.json()

    if "response" in data:
        return data["response"]
    elif "error" in data:
        return f"Ollama Error: {data['error']}"
    else:
        return f"Unexpected response: {data}"