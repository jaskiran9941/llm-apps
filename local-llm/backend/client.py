import requests
import json
from typing import Generator

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def generate_chat_response(self, model: str, messages: list[dict]) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        body = json.loads(line)
                        if "message" in body and "content" in body["message"]:
                            yield body["message"]["content"]
                        
                        if body.get("done", False):
                            break
        except requests.exceptions.RequestException as e:
            yield f"Error: Cannot connect to Ollama. Make sure it is running. Details: {str(e)}"
