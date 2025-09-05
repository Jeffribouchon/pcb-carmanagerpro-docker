# modules/agents/matching/matching_agent.py

from modules.agents.base_agent import BaseAgent
from modules.agents.contacts.contact_agent import ContactAgent
from modules.agents.vehicles.vehicle_agent import VehicleAgent


class MatchingAgent(BaseAgent):
    """
    Agent qui associe automatiquement les acheteurs (contacts)
    aux véhicules disponibles dans Odoo en fonction de leurs critères.
    """

    def __init__(self):
        self.contact_agent = ContactAgent()
        self.vehicle_agent = VehicleAgent()

    def search(self, query: str = None):
        """
        Retourne une liste de contacts enrichis avec les véhicules correspondants.
        """
        # Récupère les contacts correspondant au query (via ContactAgent)
        contacts = self.contact_agent.search(query)

        enriched_contacts = []
        for contact in contacts:
            # Construire les critères pour VehicleAgent
            criteria = {
                "Type de véhicules": contact.get("x_type_vehicule_tag_ids"),
                "Motorisation": contact.get("x_motorisation_tag_ids"),
                "Marques privilégiées": contact.get("x_marque_vehicule_tag_ids"),
                "Budget moyen": contact.get("x_budget_moyen"),
                "Kilométrage max": contact.get("x_kilometrage_max"),
            }

            # Rechercher les véhicules
            vehicles = self.vehicle_agent.search(criteria)

            # Limiter à 5 véhicules par contact
            contact["matching_vehicles"] = vehicles[:5]
            enriched_contacts.append(contact)

        return enriched_contacts
