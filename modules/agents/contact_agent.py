import json
from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client import query_deepseek
from modules.odoo.client import OdooClient
from modules.odoo.odoo_model import OdooModel

CRITERIA_PROMPT = """
Tu es un agent qui extrait des critères de recherche de contacts d’un texte utilisateur.
Les catégories attendues sont : Volume d’achat, Fréquence d’achat, Type de véhicules,
Marques privilégiées, État des véhicules, Motorisation, Kilométrage max, Budget moyen,
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

    def search(self, criteria: dict):
        domain = []
        if criteria.get("Type de véhicules"):
            domain.append(("x_type_vehicule_tag_ids", "ilike", criteria["Type de véhicules"]))
        if criteria.get("Marques privilégiées"):
            domain.append(("x_marque_vehicule_tag_ids", "ilike", criteria["Marques privilégiées"]))

        client = OdooClient()
        res_partner = OdooModel(client, 'res.partner')
        
        # Utilisation de search_read pour récupérer directement les données des contacts
        fields = ["name", "email", "phone", "city"]
        return odoo.search_read(domain, fields=fields)
