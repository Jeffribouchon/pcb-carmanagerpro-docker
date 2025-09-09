# modules/agents/matching/matching_agent.py

import re
import json
from modules.agents.base_agent import BaseAgent
from modules.agents.contacts.contact_agent import ContactAgent
from modules.agents.vehicles.vehicle_agent import VehicleAgent
from modules.utils.deepseek_client import query_deepseek, CRITERIA_PROMPT


class MatchingAgent(BaseAgent):
    """
    Agent qui associe automatiquement les acheteurs (contacts)
    aux véhicules disponibles dans Odoo en fonction de leurs critères.
    """

    def __init__(self):
        self.contact_agent = ContactAgent()
        self.vehicle_agent = VehicleAgent()

    def extract_criteria(self, query: str) -> dict:
        """Utilise DeepSeek pour transformer une requête texte en critères structurés."""
        response = query_deepseek(CRITERIA_PROMPT, query)

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

    def search(self, query: str = None):
        """
        Retourne une liste de contacts enrichis avec les véhicules correspondants.
        """
        # 🔹 Récupère les contacts correspondant à la requête (ou tous si query vide)
        extracted_criteria = self.extract_criteria(query or "")
        contacts = self.contact_agent.search(extracted_criteria)

        enriched_contacts = []
        for contact in contacts:
            # 🔹 Construire les critères pour VehicleAgent (utiliser les champs techniques Odoo)
            criteria = {
                "x_type_vehicule_tag_ids": contact.get("x_type_vehicule_tag_ids"),
                "x_motorisation_tag_ids": contact.get("x_motorisation_tag_ids"),
                "x_marque_vehicule_tag_ids": contact.get("x_marque_vehicule_tag_ids"),
                "x_budget_moyen": contact.get("x_budget_moyen"),
                "x_kilometrage_max": contact.get("x_kilometrage_max"),
            }

            # 🔹 Rechercher les véhicules correspondants
            #vehicles = self.vehicle_agent.search(criteria) or []

            # 🔹 Limiter à 5 véhicules par contact
            #contact["matching_vehicles"] = vehicles[:5]
            #enriched_contacts.append(contact)

        return enriched_contacts
