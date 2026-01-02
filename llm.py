# llm.py

import requests
from config import MODEL_NAME

# Ollama local server endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate(prompt, temperature=0.7, max_tokens=200):
    """
    Sends a prompt to the local LLM and returns its response.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    except requests.exceptions.RequestException:
        return "Error: Cannot connect to Ollama. Is it running?"

    if response.status_code != 200:
        return "Error: LLM returned a bad response."

    data = response.json()
    return data.get("response", "").strip()
