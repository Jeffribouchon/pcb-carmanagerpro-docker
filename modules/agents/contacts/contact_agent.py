import re
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

        # 🔹 Nettoyage de la réponse DeepSeek
        cleaned = response.strip()
        # enlever les balises ```json ... ```
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except Exception as e:
            raise Exception(f"Impossible de parser la réponse DeepSeek nettoyée:\n{cleaned}\nErreur: {e}")

    def search(self, criteria: dict):
        domain = []

        # Type de véhicules
        if criteria.get("Type de véhicules"):
            domain.append(("x_type_vehicule_tag_ids", "ilike", criteria["Type de véhicules"]))

        # Marques privilégiées
        if criteria.get("Marques privilégiées"):
            domain.append(("x_marque_vehicule_tag_ids", "ilike", criteria["Marques privilégiées"]))

        # Modèles de véhicules
        if criteria.get("Modèles souhaités"):
            domain.append(("x_modele_vehicule", "ilike", criteria["Marques privilégiées"]))
            
        # Volume d'achat
        if criteria.get("Volume d’achat"):
            domain.append(("x_volume_achat", "ilike", criteria["Volume d’achat"]))
    
        # Fréquence d’achat
        if criteria.get("Fréquence d’achat"):
            domain.append(("x_frequence_achat", "ilike", criteria["Fréquence d’achat"]))
    
        # État des véhicules
        if criteria.get("État des véhicules"):
            domain.append(("x_etat_vehicules", "ilike", criteria["État des véhicules"]))
    
        # Motorisation
        if criteria.get("Motorisation"):
            domain.append(("x_motorisation_tag_ids", "ilike", criteria["Motorisation"]))
    
        # Kilométrage max
        if criteria.get("Kilométrage max"):
            domain.append(("x_kilometrage_maximum", "<=", criteria["Kilométrage max"]))
    
        # Budget moyen
        if criteria.get("Budget moyen"):
            domain.append(("x_budget_maximum", "<=", criteria["Budget moyen"]))
    
        # Achat par lot
        if criteria.get("Achat par lot"):
            domain.append(("x_achat_bulk", "=", criteria["Achat par lot"].lower() == "oui"))
    
        # Mode de financement
        if criteria.get("Mode de financement"):
            domain.append(("x_mode_financement", "ilike", criteria["Mode de financement"]))
    
        # Délais de paiement
        if criteria.get("Délais de paiement"):
            domain.append(("x_delai_paiement_id", "ilike", criteria["Délais de paiement"]))
    
        # Fournisseurs habituels
        if criteria.get("Fournisseurs habituels"):
            domain.append(("x_fournisseurs_habituels", "ilike", criteria["Fournisseurs habituels"]))
    
        # Attentes principales
        if criteria.get("Attentes principales"):
            domain.append(("x_attentes", "ilike", criteria["Attentes principales"]))
    
        # Contraintes
        if criteria.get("Contraintes"):
            domain.append(("x_contraintes", "ilike", criteria["Contraintes"]))
    
        # Opportunités
        if criteria.get("Opportunités"):
            domain.append(("x_opportunites", "ilike", criteria["Opportunités"]))
    
        # Canal de contact
        if criteria.get("Canal de contact"):
            domain.append(("x_canal_contact", "ilike", criteria["Canal de contact"]))
    
        # Relation commerciale
        if criteria.get("Relation commerciale"):
            domain.append(("x_relation_commerciale", "ilike", criteria["Relation commerciale"]))

        client = OdooClient()
        res_partner = OdooModel(client, 'res.partner')
        
        # Utilisation de search_read pour récupérer directement les données des contacts
        fields = ["name", "email", "phone", "city"]
        return res_partner.search_read(domain, fields=fields)
