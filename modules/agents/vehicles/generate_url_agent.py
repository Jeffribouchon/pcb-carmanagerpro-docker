import re
import json
from urllib.parse import urlencode, quote_plus

from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client import DeepSeekClient

# CRITERIA_PROMPT = """
# Tu es un assistant spécialisé dans la génération d’url de recherche pour sites automobile. 
# Analyse le texte fourni et retourne UNIQUEMENT un JSON avec les champs demandés. 
# Pas de texte avant ou après, pas de commentaires.

# Champs attendus (si une info est manquante, retourne null) :
# - marque (string)
# - modele (string)
# - version (string)
# - carrosserie (string)
# - genre (string)
# - nb_portes (int)
# - vin (string)
# - energie (string)
# - moteur (string)
# - couleur (string)
# - immatriculation (string)
# - puissance_cv (int)
# - puissance_kw (int)
# - turbo (string)
# - boite_vitesse (string)
# - type_propulsion (string)
# - date_mec (string au format YYYY-MM-DD)
# - ktype (string)
# - numero_serie (string)

# ⚠️ RÈGLES IMPORTANTES :
# - Pour `boite_vitesse`, renvoie uniquement "Manuelle" ou "Automatique".
# - Pour `couleur`, renvoie avec seulement la première lettre en majuscule.
# - Si une valeur n’est pas présente, mets `null`.
# - Retourne uniquement l’objet JSON, sans texte supplémentaire.
# """

CRITERIA_PROMPT = """
Tu es un assistant spécialisé dans la génération d’URLs de recherche pour sites automobiles. 
À partir d’une description en langage naturel, retourne **uniquement un objet JSON** avec les sites et leurs URLs correspondantes, par exemple :
{
  "Le Bon Coin": "https://www.leboncoin.fr/recherche?category=2&price=min-10000&mileage=min-100000&u_car_brand=PEUGEOT&u_car_model=PEUGEOT_208&fuel=2&gearbox=1",
  "La Centrale": "https://www.lacentrale.fr/listing?...",
  "Autoscout24": "https://www.autoscout24.fr/lst?..."
}
⚠️ Important : 
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

    # def build_urls(self, criteria: dict) -> dict:
    #     """
    #     Construit les URLs de recherche pour différents sites automobiles
    #     à partir des critères extraits.
    #     """

    #     urls = {}

    #     # --- Le Bon Coin ---
    #     lbc_params = {}
    #     if criteria.get("marque"):
    #         lbc_params["brand"] = criteria["marque"]
    #     if criteria.get("modele"):
    #         lbc_params["model"] = criteria["modele"]
    #     if criteria.get("energie"):
    #         lbc_params["fuel"] = criteria["energie"].lower()
    #     if criteria.get("boite_vitesse"):
    #         lbc_params["gearbox"] = (
    #             "manual" if criteria["boite_vitesse"] == "Manuelle" else "automatic"
    #         )
    #     urls["leboncoin"] = "https://www.leboncoin.fr/recherche?" + urlencode(lbc_params, quote_via=quote_plus)

    #     # --- La Centrale ---
    #     lc_params = {}
    #     if criteria.get("marque"):
    #         lc_params["makesModelsCommercialNames"] = f"{criteria['marque']}::{criteria.get('modele', '')}"
    #     if criteria.get("energie"):
    #         lc_params["fuels"] = criteria["energie"].upper()
    #     if criteria.get("boite_vitesse"):
    #         lc_params["gearbox"] = criteria["boite_vitesse"].upper()
    #     urls["lacentrale"] = "https://www.lacentrale.fr/listing?" + urlencode(lc_params, quote_via=quote_plus)

    #     # --- Autoscout24 (bonus si tu veux élargir) ---
    #     as24_params = {}
    #     if criteria.get("marque"):
    #         as24_params["make"] = criteria["marque"]
    #     if criteria.get("modele"):
    #         as24_params["model"] = criteria["modele"]
    #     if criteria.get("energie"):
    #         as24_params["fuel"] = criteria["energie"].lower()
    #     urls["autoscout24"] = "https://www.autoscout24.fr/lst?" + urlencode(as24_params, quote_via=quote_plus)

    #     return urls

    def search(self, criteria: dict):
        """
        Analyse une demande en langage naturel et crée une liste d’urls de recherche.
        """
        # urls = self.build_urls(criteria)
        urls = criteria
        return urls
