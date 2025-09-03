import json
from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client import query_deepseek
from modules.odoo.odoo_model import OdooModel

CRITERIA_PROMPT = """
Tu es un agent qui extrait des critères de recherche de contacts d’un texte utilisateur.
Réponds uniquement en JSON avec les clés suivantes :
Volume d’achat, Fréquence d’achat, Type de véhicules, Marques privilégiées,
État des véhicules, Motorisation, Kilométrage max, Budget moyen, Achat par lot,
Mode de financement, Délais de paiement, Fournisseurs habituels, Attentes principales,
Contraintes, Opportunités, Canal de contact, Relation commerciale.
"""

FILTER_PROMPT = """
Tu es un agent qui reçoit une liste de contacts (JSON) et des critères de recherche (JSON).
Retourne uniquement les contacts qui correspondent le mieux aux critères.
Réponds uniquement avec un tableau JSON des contacts retenus (pas de texte explicatif).
"""

class ContactAgent(BaseAgent):

    def extract_criteria(self, query: str) -> dict:
        response = query_deepseek(CRITERIA_PROMPT, query)
        try:
            return json.loads(response)
        except:
            raise Exception(f"Impossible de parser la réponse DeepSeek: {response}")

    def hybrid_search(self, query: str):
        # 1. Extraction des critères
        criteria = self.extract_criteria(query)

        # 2. Pré-filtrage côté Odoo (domain sur les champs clés)
        domain = []
        if criteria.get("Type de véhicules"):
            domain.append(("x_vehicle_type", "ilike", criteria["Type de véhicules"]))
        if criteria.get("Motorisation"):
            domain.append(("x_fuel_type", "ilike", criteria["Motorisation"]))
        if criteria.get("Marques privilégiées"):
            domain.append(("x_preferred_brands", "ilike", criteria["Marques privilégiées"]))

        odoo = OdooModel("res.partner")

        # récupérer un set large mais limité
        fields = [
            "name", "email", "phone", "city", "x_vehicle_type", "x_preferred_brands",
            "x_purchase_volume", "x_purchase_frequency", "x_vehicle_state", "x_fuel_type",
            "x_max_km", "x_budget", "x_bulk_purchase", "x_payment_mode", "x_payment_terms",
            "x_current_suppliers", "x_expectations", "x_constraints", "x_opportunities",
            "x_contact_channel", "x_commercial_relationship"
        ]
        pre_filtered = odoo.search_read(domain, fields=fields, limit=200)

        # 3. Raffinage via DeepSeek
        filtering_input = {
            "criteria": criteria,
            "contacts": pre_filtered
        }
        refined_response = query_deepseek(FILTER_PROMPT, json.dumps(filtering_input, ensure_ascii=False))
        try:
            refined_contacts = json.loads(refined_response)
        except:
            refined_contacts = pre_filtered  # fallback si DeepSeek échoue

        return criteria, refined_contacts
    
    def search(self, query: str):
        return self.hybrid_search(query)
