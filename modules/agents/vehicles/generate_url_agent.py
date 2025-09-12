import re
import json
import requests
from urllib.parse import urlencode, quote_plus

from modules.agents.base_agent import BaseAgent
from modules.agents.scraping import scrape_lacentrale, scrape_leboncoin
from modules.utils.deepseek_client import DeepSeekClient

CRITERIA_PROMPT = """
Tu es un assistant spécialisé dans la génération d’URLs de recherche pour sites automobiles.
À partir d’une description en langage naturel, retourne uniquement un objet JSON avec les sites et leurs URLs correspondantes.

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

### Exemples

Entrée :
"Je cherche une Peugeot 208 essence, boîte manuelle, moins de 100 000 km, pour moins de 10 000 €."

Sortie :
{
  "Le Bon Coin": "https://www.leboncoin.fr/recherche?category=2&price=0-10000&mileage=0-100000&u_car_brand=PEUGEOT&u_car_model=PEUGEOT_208&fuel=1&gearbox=1",
  "La Centrale": "https://www.lacentrale.fr/listing?makesModelsCommercialNames=PEUGEOT%3A208&priceMax=10000&kilometerMax=100000&fuels=essence&gearboxes=manuelle",
  "Autoscout24": "https://www.autoscout24.fr/lst/peugeot/208?atype=C&cy=F&damaged_listing=exclude&desc=0&fuel=B&gear=M&kmto=100000&powertype=kw&priceto=10000&priceTo=999999&search_id=1oicjv5uo3v&sort=standard&ustate=N%2CU",
  "PlatformCars B2B": "https://www.platformcars-b2b.com/shop"
}

Entrée :
"BMW X3 diesel automatique entre 2018 et 2022."

Sortie :
{
  "Le Bon Coin": "https://www.leboncoin.fr/recherche?category=2&price=0-999999&mileage=0-200000&u_car_brand=BMW&u_car_model=BMW_X3&fuel=3&gearbox=2&regdate=2018-2022",
  "La Centrale": "https://www.lacentrale.fr/listing?makesModelsCommercialNames=BMW%3AX3&priceMax=999999&kilometerMax=200000&years=2018-2022&fuels=diesel&gearboxes=automatique",
  "Autoscout24": "https://www.autoscout24.fr/lst/bmw/x3?atype=C&cy=F&damaged_listing=exclude&desc=0&fregfrom=2018&fregto=2022&fuel=D&gear=A&powertype=kw&priceTo=999999&search_id=o6way7nesc&sort=standard&ustate=N%2CU",
  "PlatformCars B2B": "https://www.platformcars-b2b.com/shop"
}

Entrée :
"Renault Clio toutes motorisations, budget max 5000 €, peu importe l'année."

Sortie :
{
  "Le Bon Coin": "https://www.leboncoin.fr/recherche?category=2&price=0-5000&mileage=0-200000&u_car_brand=RENAULT&u_car_model=RENAULT_CLIO",
  "La Centrale": "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3ACLIO&priceMax=5000&kilometerMax=200000",
  "Autoscout24": "https://www.autoscout24.fr/lst/renault/clio/pr_5000?atype=C&cy=F&damaged_listing=exclude&desc=0&powertype=kw&priceTo=999999&search_id=2cb8asenjht&sort=standard&ustate=N%2CU",
  "PlatformCars B2B": "https://www.platformcars-b2b.com/shop"
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

        if "PlatformCars B2B" in urls:
            ads = search_platformcars_b2b(urls["PlatformCars B2B"], limit=10)
        
        return urls, ads
