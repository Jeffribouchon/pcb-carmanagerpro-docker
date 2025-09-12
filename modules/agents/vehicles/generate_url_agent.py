import re
import json
import requests
from urllib.parse import urlencode, quote_plus

from modules.agents.base_agent import BaseAgent
from modules.agents.scraping import scrape_lacentrale, scrape_leboncoin
from modules.utils.deepseek_client import DeepSeekClient

CRITERIA_PROMPT = """
Tu es un assistant spécialisé dans la génération d’URLs de recherche pour sites automobiles. 
À partir d’une description en langage naturel, retourne **uniquement un objet JSON** avec les sites et leurs URLs correspondantes, par exemple :
{
  "Le Bon Coin": "https://www.leboncoin.fr/recherche?category=2&price=min-10000&mileage=min-100000&u_car_brand=PEUGEOT&u_car_model=PEUGEOT_208&fuel=2&gearbox=1",
  "La Centrale": "https://www.lacentrale.fr/listing?...",
  "Autoscout24": "https://www.autoscout24.fr/lst?..."
}
⚠️ RÈGLES IMPORTANTES :
- Retourne uniquement le JSON, sans texte ni explication.
- Si une information est manquante, utilise des valeurs par défaut raisonnables.
"""


class GenerateUrlAgent(BaseAgent):

    def extract_criteria(self, query: str) -> dict:
        """Utilise DeepSeek pour transformer une requête texte en critères structurés."""
        response = DeepSeekClient(CRITERIA_PROMPT, query)

        # 🔹 Nettoyage de la réponse DeepSeek
        cleaned = response.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except Exception as e:
            raise Exception(
                f"Impossible de parser la réponse DeepSeek nettoyée:\n{cleaned}\nErreur: {e}"
            )

    def search(self, criteria: dict):
        """
        Analyse une demande en langage naturel et crée une liste d’urls de recherche.
        """
        ads = None

        urls = criteria
        # if "Le Bon Coin" in urls:
        #        ads = scrape_leboncoin(urls["Le Bon Coin"], limit=10)
      
        # if "La centrale" in urls:
        #     ads = scrape_lacentrale(urls["La centrale"], limit=10)
        
        return urls, ads
