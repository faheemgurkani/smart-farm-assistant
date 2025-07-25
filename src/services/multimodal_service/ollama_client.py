import requests

def generate_response(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma3n:e4b",  # adjust to whatever you're using
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"Error from Ollama: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        print("Exception while connecting to Ollama:", e)
        return ""
