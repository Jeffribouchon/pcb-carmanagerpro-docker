import requests
import os

DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def query_deepseek(system_prompt: str, user_query: str, temperature: float = 0.2) -> str:
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    # payload = {
    #     "model": "deepseek-chat",
    #     "messages": [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_query}
    #     ],
    #     "temperature": temperature
    # }
    payload = {
        "model": "deepseek-v1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": 1000
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
