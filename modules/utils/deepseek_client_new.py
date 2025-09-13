import os
import requests

class DeepSeekClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        # On enlève le / final si présent pour éviter les doublons
        base_url = (api_url or os.getenv("DEEPSEEK_API_URL") or "").rstrip("/")
        self.api_url_completions = f"{base_url}/chat/completions"
        self.api_url_balance = f"{base_url}/user/balance"
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        if not base_url or not self.api_key:
            raise ValueError("⚠️ DeepSeek API URL et/ou API KEY manquants")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Appelle l'API DeepSeek pour générer une réponse basée sur un prompt."""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(self.api_url_completions, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def balance(self) -> dict:
        """Récupère la balance de ton compte via l'API DeepSeek."""
        response = requests.get(self.api_url_balance, headers=self.headers)
        response.raise_for_status()
        return response.json()
