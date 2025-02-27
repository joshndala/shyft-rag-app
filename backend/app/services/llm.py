import requests
from fastapi.responses import StreamingResponse
import os
from app.config import config

OPENROUTER_API_KEY = config.OPENROUTER_API_KEY

def ask_llm(question, context):
    """Sends question and context to OpenRouter AI."""
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    data = {
        "model": "mistral",
        "messages": [
            {"role": "system", "content": "You are an AI answering questions based on provided documents."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
        ],
        "stream": True
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers, stream=True)
    return StreamingResponse(response.iter_content(chunk_size=1024), media_type="text/plain")