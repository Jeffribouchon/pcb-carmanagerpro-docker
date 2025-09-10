import re
import json
from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client  import DeepSeekClient 

CRITERIA_PROMPT = """
        Tu es un assistant spécialisé dans la génération d’url de recherche pour sites automobile. 
        Analyse le texte fourni et retourne UNIQUEMENT un JSON d’urls valides. 
        Pas de texte avant ou après, pas de commentaires.

        Champs attendus (si une info est manquante, retourne null) :
        - marque (string)
        - modele (string)
        - version (string)
        - carrosserie (string)
        - genre (string)
        - nb_portes (int)
        - vin (string)
        - energie (string)
        - moteur (string)
        - couleur (string)
        - immatriculation (string)
        - puissance_cv (int)
        - puissance_kw (int)
        - turbo (string)
        - boite_vitesse (string)
        - type_propulsion (string)
        - date_mec (string au format YYYY-MM-DD)
        - ktype (string)
        - numero_serie (string)

        ⚠️ Important : 
        - Pour `boite_vitesse`, renvoie uniquement "Manuelle" ou "Automatique".
        - Pour `couleur`, renvoie avec seulement la première lettre en majuscule.
        - Si une valeur n’est pas présente, mets `null`.
        - Retourne uniquement l’objet JSON, sans texte supplémentaire.
        Texte à analyser :
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
            
    def search(self, criteria: str):
        """
        Analyse une demande et crée une liste d’url
        """
        # 3. Générer la liste d’urls
  
        return None
