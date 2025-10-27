import requests
from config import OLLAMA_API_URL, MODEL_NAME

def ask_llm(prompt):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=300   # increase timeout for long first-run
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response received.")
        else:
            return f"LLM error {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return "LLM request timed out. Try restarting Ollama or reducing prompt size."
    except Exception as e:
        return f"LLM request failed: {str(e)}"
