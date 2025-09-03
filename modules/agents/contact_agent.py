import json
from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client import query_deepseek
from modules.odoo.client import OdooClient
from modules.odoo.odoo_model import OdooModel

CRITERIA_PROMPT = """
Tu es un agent qui extrait des critères de recherche de contacts d’un texte utilisateur.
Les catégories attendues sont : Volume d’achat, Fréquence d’achat, Type de véhicules,
Marques privilégiées, Modèles souhaités, État des véhicules, Motorisation, Kilométrage max, Budget moyen,
Achat par lot, Mode de financement, Délais de paiement, Fournisseurs habituels,
Attentes principales, Contraintes, Opportunités, Canal de contact, Relation commerciale.
Réponds uniquement en JSON.
"""

class ContactAgent(BaseAgent):

    def extract_criteria(self, query: str) -> dict:
        response = query_deepseek(CRITERIA_PROMPT, query)
        try:
            return json.loads(response)
        except:
            raise Exception(f"Impossible de parser la réponse DeepSeek: {response}")

    def prefilter_contacts(self, criteria: dict):
        domain = []
        client = OdooClient()
        res_partner = OdooModel(client, 'res.partner')
        
        # Motorisation
        if criteria.get("Motorisation"):
            domain.append(("x_motorisation_tag_ids", "ilike", criteria["Motorisation"]))
    
        # Kilométrage max
        if criteria.get("Kilométrage max"):
            domain.append(("x_kilometrage_maximum", "<=", criteria["Kilométrage max"]))
    
        # Budget moyen
        if criteria.get("Budget moyen"):
            domain.append(("x_budget_maximum", "<=", criteria["Budget moyen"]))

        # Utilisation de search_read pour récupérer directement les données des contacts
        fields = ["name", "email", "phone", "city"]
        return res_partner.search_read(domain, fields=fields)

    #🔹 Étape 2 : DeepSeek raffine
    def refine_with_ai(query: str, contacts: list) -> list:
    #     prompt = f"""
    # Tu es un assistant qui doit filtrer une liste de contacts Odoo selon cette requête utilisateur :
    # "{query}"
    
    # Voici les contacts disponibles (JSON) :
    # {json.dumps(contacts, ensure_ascii=False)}
    
    # Retourne uniquement les contacts pertinents en JSON (garde tous leurs champs).
    # Si aucun ne correspond, retourne [].
    # """
        prompt = f"""
    Tu es un assistant qui doit filtrer une liste de contacts Odoo selon cette requête utilisateur
    Retourne uniquement les contacts pertinents en JSON (garde tous leurs champs).
    Si aucun ne correspond, retourne [].
    """
        response = query_deepseek(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def search(self, criteria: dict):
        # 1. Extraire les critères
        # criteria = self.extract_criteria(query)

        # 2. Pré-filtrer côté Odoo
        prefiltered = self.prefilter_contacts(criteria)

        if not prefiltered:
            return criteria, []

        # 3. Raffiner côté IA
        # refined = [] #refine_with_ai(query, prefiltered)

        return prefiltered
        # return criteria, refined
    

    

