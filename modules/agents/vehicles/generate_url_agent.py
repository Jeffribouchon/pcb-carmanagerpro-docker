import re
import json
import requests
from urllib.parse import urlencode, quote_plus

from modules.agents.base_agent import BaseAgent
from modules.agents.scraping import scrape_lacentrale, scrape_leboncoin, search_platformcars_b2b
from modules.utils.deepseek_client import DeepSeekClient

CRITERIA_PROMPT = """
Tu es un assistant spécialisé dans la génération d’URLs de recherche pour sites automobiles. 
À partir d’une description en langage naturel, retourne uniquement un objet JSON avec les sites, leurs URLs correspondantes, et les critères utilisés pour générer chaque URL.

⚠️ RÈGLES IMPORTANTES :
- Retourne uniquement le JSON, sans texte ni explication.
- Toujours encoder correctement les espaces et caractères spéciaux dans les URLs.
- Si une information est manquante, utilise les valeurs par défaut suivantes :
    - Prix max → très élevé (price=0-999999 ou priceTo=999999)
    - Kilométrage max → aucune (pas de filtre)
    - Année min → aucune (regdate= vide ou pas d’argument)
    - Carburant → toutes motorisations (pas de filtre)
    - Boîte de vitesse → manuelle + automatique (pas de filtre)

### Correspondances à utiliser

Le Bon Coin :
- category=2 → Voitures
- price=min-max → Prix en €
- mileage=min-max → Kilométrage en km
- regdate=min-max → Année de mise en circulation
- u_car_brand → Marque (ex. PEUGEOT, BMW, RENAULT)
- u_car_model → Modèle (ex. PEUGEOT_208, BMW_X3)
- fuel → Carburant
    1 = Essence
    2 = Hybride essence
    3 = Diesel
    4 = Hybride diesel
    5 = Électrique
    6 = GPL
    7 = Éthanol
- gearbox → Boîte de vitesse
    1 = Manuelle
    2 = Automatique

La Centrale :
- makesModelsCommercialNames=MARQUE%3AMODELE (ex. PEUGEOT%3A208)
- priceMax=XXXX
- kilometerMax=XXXX
- years=AAAA-AAAA
- fuels → essence, diesel, electrique, hybride, gpl
- gearboxes → manuelle, automatique

Autoscout24 :
- atype=C (toujours)
- make=marque, model=modèle (ou via /lst/marque/modèle)
- priceTo=XXXX
- kmto=XXXX
- fregfrom=AAAA, fregto=AAAA
- fuel → petrol, diesel, electric, hybrid, cng, lpg
- gear → manual, automatic

PlatformCars B2B :
⚠️ Toujours retourner l'URL générique :
https://www.platformcars-b2b.com/shop
Ne pas ajouter de paramètres dans l'URL.
Inclure seulement les critères utilisés dans le champ "criteria".

### Exemple de sortie JSON

Entrée :
"Je cherche une Peugeot 208 essence, boîte manuelle, moins de 100 000 km, pour moins de 10 000 €."

Sortie :
{
  "Le Bon Coin": {
    "url": "https://www.leboncoin.fr/recherche?category=2&price=0-10000&mileage=0-100000&u_car_brand=PEUGEOT&u_car_model=PEUGEOT_208&fuel=1&gearbox=1",
    "criteria": {
      "brand": "PEUGEOT",
      "model": "208",
      "fuel": "essence",
      "gearbox": "manuelle",
      "mileage_max": 100000,
      "price_max": 10000
    }
  },
  "La Centrale": {
    "url": "https://www.lacentrale.fr/listing?makesModelsCommercialNames=PEUGEOT%3A208&priceMax=10000&kilometerMax=100000&fuels=essence&gearboxes=manuelle",
    "criteria": {
      "brand": "PEUGEOT",
      "model": "208",
      "fuel": "essence",
      "gearbox": "manuelle",
      "mileage_max": 100000,
      "price_max": 10000
    }
  },
  "Autoscout24": {
    "url": "https://www.autoscout24.fr/lst/peugeot/208?atype=C&cy=F&damaged_listing=exclude&desc=0&fuel=B&gear=M&kmto=100000&powertype=kw&priceto=10000&priceTo=999999&search_id=1oicjv5uo3v&sort=standard&ustate=N%2CU",
    "criteria": {
      "brand": "PEUGEOT",
      "model": "208",
      "fuel": "essence",
      "gearbox": "manuelle",
      "mileage_max": 100000,
      "price_max": 10000
    }
  },
  "PlatformCars B2B": {
    "url": "https://www.platformcars-b2b.com/shop",
    "criteria": {
      "brand": "PEUGEOT",
      "model": "208",
      "fuel": "essence",
      "gearbox": "manuelle",
      "mileage_max": 100000,
      "price_max": 10000
    }
  }
}
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

    def search(self, urls_json: dict):
        """
        Analyse une demande en langage naturel et crée une liste d’ads à partir des URLs générées.
        
        criteria : dictionnaire JSON généré par l'agent AI, avec la structure :
            {
                "Le Bon Coin": {"url": "...", "criteria": {...}},
                "La Centrale": {"url": "...", "criteria": {...}},
                "Autoscout24": {"url": "...", "criteria": {...}},
                "PlatformCars B2B": {"url": "...", "criteria": {...}}
            }
        """
        ads = []  # liste vide pour cumuler tous les résultats
        urls = {}

        for site, data in urls_json.items():
            if isinstance(data, dict) and "url" in data:
                urls[site] = data["url"]

      # Scraping Le Bon Coin, La Centrale, Autoscout24 avec l'URL
      # if "Le Bon Coin" in criteria:
      #     leboncoin_ads = scrape_leboncoin(urls_json["Le Bon Coin"]["url"], limit=10)
      #     ads.extend(leboncoin_ads)

      # if "La Centrale" in criteria:
      #     lacentrale_ads = scrape_lacentrale(urls_json["La Centrale"]["url"], limit=10)
      #     ads.extend(lacentrale_ads)

      # if "Autoscout24" in criteria:
      #     autoscout_ads = scrape_autoscout24(urls_json["Autoscout24"]["url"], limit=10)
      #     ads.extend(autoscout_ads)

      # Searching PlatformCars B2B avec les critères
        if "PlatformCars B2B" in urls_json:
            platformcars_ads = search_platformcars_b2b(urls_json["PlatformCars B2B"]["criteria"], limit=10)
            ads.extend(platformcars_ads)
            
        return urls, ads

    # def search(self, urls_json: dict):
    #     """
    #     Analyse une demande en langage naturel et crée une liste d’ads à partir des URLs générées.
        
    #     criteria : dictionnaire JSON généré par l'agent AI, avec la structure :
    #         {
    #             "Le Bon Coin": {"url": "...", "criteria": {...}},
    #             "La Centrale": {"url": "...", "criteria": {...}},
    #             "Autoscout24": {"url": "...", "criteria": {...}},
    #             "PlatformCars B2B": {"url": "...", "criteria": {...}}
    #         }
    #     """
    #     results = {}  # dictionnaire final à retourner
    
    #     for site, data in urls_json.items():
    #         # Initialisation du site avec l'URL et une liste vide d'annonces
    #         site_entry = {
    #             "url": data.get("url", "#"),
    #             "ads_results": []
    #         }
            
    #         # Scraping Le Bon Coin, La Centrale, Autoscout24 avec l'URL
    #         # if "Le Bon Coin" in criteria:
    #         #     leboncoin_ads = scrape_leboncoin(urls_json["Le Bon Coin"]["url"], limit=10)
    #         #     ads.extend(leboncoin_ads)
      
    #         # if "La Centrale" in criteria:
    #         #     lacentrale_ads = scrape_lacentrale(urls_json["La Centrale"]["url"], limit=10)
    #         #     ads.extend(lacentrale_ads)
      
    #         # if "Autoscout24" in criteria:
    #         #     autoscout_ads = scrape_autoscout24(urls_json["Autoscout24"]["url"], limit=10)
    #         #     ads.extend(autoscout_ads)

    #         # Si c'est PlatformCars B2B, chercher les annonces
    #         if site == "PlatformCars B2B" and "criteria" in data:
    #             platformcars_ads = search_platformcars_b2b(data["criteria"], limit=10)
    #             site_entry["ads_results"].extend(platformcars_ads)
    
    #         results[site] = site_entry
    
    #     return results

