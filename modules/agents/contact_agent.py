import re
import json
from modules.agents.base_agent import BaseAgent
from modules.utils.deepseek_client import query_deepseek
from modules.odoo.client import OdooClient
from modules.odoo.odoo_model import OdooModel

CRITERIA_PROMPT = """
Tu es un agent qui extrait des critères de recherche de contacts d’un texte utilisateur.
Réponds uniquement en JSON avec les clés suivantes :
Volume d’achat, Fréquence d’achat, Type de véhicules, Marques privilégiées,
État des véhicules, Motorisation, Kilométrage max, Budget moyen, Achat par lot,
Mode de financement, Délais de paiement, Fournisseurs habituels, Attentes principales,
Contraintes, Opportunités, Canal de contact, Relation commerciale, Notes.
"""

FILTER_PROMPT = """
Tu es un agent qui reçoit une liste de contacts (JSON) et des critères de recherche (JSON).
Retourne uniquement les contacts qui correspondent le mieux aux critères.
Réponds uniquement avec un tableau JSON des contacts retenus (pas de texte explicatif).
"""

class ContactAgent(BaseAgent):

    def __init__(self):
        client = OdooClient()
        self.res_partner = OdooModel(client, 'res.partner')
    
    def extract_criteria(self, query: str) -> dict:
        response = query_deepseek(CRITERIA_PROMPT, query)

        # 🔹 Nettoyage de la réponse DeepSeek
        cleaned = response.strip()
        # enlever les balises ```json ... ```
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except Exception as e:
            raise Exception(f"Impossible de parser la réponse DeepSeek nettoyée:\n{cleaned}\nErreur: {e}")
    
    def hybrid_search(self, query: str):
        # 1. Extraction des critères
        criteria = self.extract_criteria(query)

        # 2. Pré-filtrage côté Odoo (domain sur les champs clés)
        domain = []
        
        domain.append('|')
        domain.append(('category_id', '=', False))
        domain.append(('category_id.name', 'not in', ['Test', 'Partenaires']))
        
        if criteria.get("Type de véhicules"):
            domain.append(("x_type_vehicule_tag_ids", "ilike", criteria["Type de véhicules"]))
        if criteria.get("Motorisation"):
            domain.append(("x_motorisation_tag_ids.x_name", "ilike", criteria["Motorisation"]))
        if criteria.get("Marques privilégiées"):
            domain.append(("x_marque_vehicule_tag_ids.x_name", "ilike", criteria["Marques privilégiées"]))

        # récupérer un set large mais limité
        fields = [
            "name", "email", "phone", "city", "x_statut_client", "x_type_vehicule_tag_ids", "x_marque_vehicule_tag_ids.x_name", "x_modele_vehicule",
            "x_motorisation_tag_ids.x_name", "x_volume_achat", "x_frequence_achat", "x_etat_vehicules",
            "x_kilometrage_maximum", "x_annee_minimum", "x_budget_maximum", "x_achat_bulk", "x_mode_financement", "x_mode_paiement", "x_delai_paiement_id.name",
            "x_fournisseurs_habituels", "x_attentes", "x_contraintes", "x_opportunites",
            "x_canal_contact", "x_relation_commerciale", "x_remarques_specifiques", "comment"
        ]
        pre_filtered = self.res_partner.search_read(domain, fields=fields, limit=200)

        # 3. Raffinage via DeepSeek
        # refined_contacts = pre_filtered
        filtering_input = {
            "criteria": criteria,
            "contacts": pre_filtered
        }
        refined_response = query_deepseek(FILTER_PROMPT, json.dumps(filtering_input, ensure_ascii=False))
        try:
            refined_contacts = json.loads(refined_response)
        except:
            refined_contacts = pre_filtered  # fallback si DeepSeek échoue

        # ✅ Retourne les critères et contacts
        return (criteria, refined_contacts)
    
    def search(self, query: str):
        return self.hybrid_search(query)
