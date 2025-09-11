import re
import json
from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client import DeepSeekClient
from modules.odoo.client import OdooClient
from modules.odoo.odoo_model import OdooModel

CRITERIA_PROMPT = """
Tu es un agent qui extrait des critères de recherche de véhicules à partir d'une demande acheteur.
Réponds uniquement en JSON avec les clés suivantes :
Type de véhicules, Marques privilégiées, Modèle de véhicule, Motorisation,
Kilométrage max, Budget max, Achat par lot, Opportunités.
"""

class VehicleAgent(BaseAgent):

    def __init__(self):
        client = OdooClient()
        self.product_template = OdooModel(client, 'product.template')

    def extract_criteria(self, query: str) -> dict:
        response = DeepSeekClient(CRITERIA_PROMPT, query)

        # Nettoyer la réponse
        cleaned = response.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except Exception as e:
            raise Exception(f"Impossible de parser la réponse DeepSeek nettoyée:\n{cleaned}\nErreur: {e}")

    def search(self, criteria: dict):

        domain = []

        if criteria.get("Type de véhicules"):
            domain.append(("x_studio_type_de_vhicule", "ilike", criteria["Type de véhicules"]))
        if criteria.get("Marques privilégiées"):
            domain.append(("x_studio_marque", "ilike", criteria["Marques privilégiées"]))
        if criteria.get("Modèle de véhicule"):
            domain.append(("x_studio_modele", "ilike", criteria["Modèle de véhicule"]))
        if criteria.get("Motorisation"):
            domain.append(("x_studio_energie", "ilike", criteria["Motorisation"]))
        if criteria.get("Kilométrage max"):
            try:
                km = int(re.sub(r"\D", "", criteria["Kilométrage max"]))
                domain.append(("x_studio_integer_field_hm_1iqqfg2td", "<=", km))
            except:
                pass
        if criteria.get("Budget max"):
            try:
                budget = int(re.sub(r"\D", "", criteria["Budget max"]))
                domain.append(("list_price", "<=", budget))
            except:
                pass

        fields = [
            "name", "list_price", "x_studio_type_de_vhicule", "x_studio_modele", "x_studio_marque",
            "x_studio_energie", "x_studio_integer_field_hm_1iqqfg2td"
        ]

        results = self.product_template.search_read(domain, fields=fields, limit=100)

        return criteria, results
