
# modules/agents/contacts/cleanup_agent.py

from modules.agents.base_agent import BaseAgent
from modules.odoo.odoo_model import OdooModel


class CleanupAgent(BaseAgent):
    """
    Agent IA pour détecter les doublons dans Odoo
    - res.partner (contacts)
    - product.template (véhicules)
    """

    def search(self, query: str = None):
        """
        Exécute la recherche des doublons.
        Le paramètre `query` est optionnel (pas utilisé pour le nettoyage).
        Retourne un dictionnaire { "contacts": [...], "vehicles": [...] }
        """
        results = {
            "contacts": self._find_contact_duplicates(),
            "vehicles": self._find_vehicle_duplicates(),
        }
        return results

    def _find_contact_duplicates(self):
        partner_model = OdooModel("res.partner")
        fields = ["id", "name", "email", "phone", "city"]

        # On récupère tous les contacts (limit = 500 pour éviter surcharge)
        contacts = partner_model.search_read([], fields=fields, limit=500)

        duplicates = []
        seen = {}

        for contact in contacts:
            key = None
            if contact.get("email"):
                key = ("email", contact["email"].lower())
            elif contact.get("phone"):
                key = ("phone", contact["phone"])
            elif contact.get("name") and contact.get("city"):
                key = ("name_city", f"{contact['name'].lower()}_{contact['city'].lower()}")

            if key:
                if key in seen:
                    duplicates.append((seen[key], contact))
                else:
                    seen[key] = contact

        return duplicates

    def _find_vehicle_duplicates(self):
        vehicle_model = OdooModel("product.template")
        fields = ["id", "name", "x_immat", "x_marque", "x_modele", "x_annee"]

        vehicles = vehicle_model.search_read([], fields=fields, limit=500)

        duplicates = []
        seen = {}

        for v in vehicles:
            key = None
            if v.get("x_immat"):
                key = ("immat", v["x_immat"].replace(" ", "").upper())
            elif v.get("x_marque") and v.get("x_modele") and v.get("x_annee"):
                key = ("car", f"{v['x_marque']}_{v['x_modele']}_{v['x_annee']}")

            if key:
                if key in seen:
                    duplicates.append((seen[key], v))
                else:
                    seen[key] = v

        return duplicates
