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


    def search(self, query: str):
        # 1. Extraire les critères
        # criteria = self.extract_criteria(query)

        # 2. Pré-filtrer côté Odoo
        prefiltered = prefilter_contacts(criteria)

        # if not prefiltered:
        #     return criteria, []

        # 3. Raffiner côté IA
        # refined = [] #refine_with_ai(query, prefiltered)

        return prefiltered
        # return criteria, refined

    
    

    # # 🔹 Étape 1 : Odoo fait le pré-filtrage
    # def prefilter_contacts(self, criteria: dict):
    #     domain = []
    #     client = OdooClient()
    #     res_partner = OdooModel(client, 'res.partner')

    #     # Type de véhicules
    #     if criteria.get("Type de véhicules"):
    #         domain.append(("x_type_vehicule_tag_ids", "ilike", criteria["Type de véhicules"]))

    #     # Marques privilégiées
    #     if criteria.get("Marques privilégiées"):
    #         domain.append(("x_marque_vehicule_tag_ids", "ilike", criteria["Marques privilégiées"]))

    #     # Modèles de véhicules
    #     if criteria.get("Modèles souhaités"):
    #         domain.append(("x_modele_vehicule", "ilike", criteria["Marques privilégiées"]))
            
    #     # Volume d'achat
    #     if criteria.get("Volume d’achat"):
    #         domain.append(("x_volume_achat", "ilike", criteria["Volume d’achat"]))
    
    #     # Fréquence d’achat
    #     if criteria.get("Fréquence d’achat"):
    #         domain.append(("x_frequence_achat", "ilike", criteria["Fréquence d’achat"]))
    
    #     # État des véhicules
    #     if criteria.get("État des véhicules"):
    #         domain.append(("x_etat_vehicules", "ilike", criteria["État des véhicules"]))
    
    #     # Motorisation
    #     if criteria.get("Motorisation"):
    #         domain.append(("x_motorisation_tag_ids", "ilike", criteria["Motorisation"]))
    
    #     # Kilométrage max
    #     if criteria.get("Kilométrage max"):
    #         domain.append(("x_kilometrage_maximum", "<=", criteria["Kilométrage max"]))
    
    #     # Budget moyen
    #     if criteria.get("Budget moyen"):
    #         domain.append(("x_budget_maximum", "<=", criteria["Budget moyen"]))
    
    #     # Achat par lot
    #     if criteria.get("Achat par lot"):
    #         domain.append(("x_achat_bulk", "=", criteria["Achat par lot"].lower() == "oui"))
    
    #     # Mode de financement
    #     if criteria.get("Mode de financement"):
    #         domain.append(("x_mode_financement", "ilike", criteria["Mode de financement"]))
    
    #     # Délais de paiement
    #     if criteria.get("Délais de paiement"):
    #         domain.append(("x_delai_paiement_id", "ilike", criteria["Délais de paiement"]))
    
    #     # Fournisseurs habituels
    #     if criteria.get("Fournisseurs habituels"):
    #         domain.append(("x_fournisseurs_habituels", "ilike", criteria["Fournisseurs habituels"]))
    
    #     # Attentes principales
    #     if criteria.get("Attentes principales"):
    #         domain.append(("x_attentes", "ilike", criteria["Attentes principales"]))
    
    #     # Contraintes
    #     if criteria.get("Contraintes"):
    #         domain.append(("x_contraintes", "ilike", criteria["Contraintes"]))
    
    #     # Opportunités
    #     if criteria.get("Opportunités"):
    #         domain.append(("x_opportunites", "ilike", criteria["Opportunités"]))
    
    #     # Canal de contact
    #     if criteria.get("Canal de contact"):
    #         domain.append(("x_canal_contact", "ilike", criteria["Canal de contact"]))
    
    #     # Relation commerciale
    #     if criteria.get("Relation commerciale"):
    #         domain.append(("x_relation_commerciale", "ilike", criteria["Relation commerciale"]))

        
    #     # Utilisation de search_read pour récupérer directement les données des contacts
    #     fields = ["name", "email", "phone", "city"]
    #     return res_partner.search_read(domain, fields=fields)
    
    # def search(self, query: str):
    #     # 1. Extraire les critères
    #     criteria = self.extract_criteria(query)
    #     return criteria
    
    # #🔹 Étape 2 : DeepSeek raffine
    # def refine_with_ai(query: str, contacts: list) -> list:
    # #     prompt = f"""
    # # Tu es un assistant qui doit filtrer une liste de contacts Odoo selon cette requête utilisateur :
    # # "{query}"
    
    # # Voici les contacts disponibles (JSON) :
    # # {json.dumps(contacts, ensure_ascii=False)}
    
    # # Retourne uniquement les contacts pertinents en JSON (garde tous leurs champs).
    # # Si aucun ne correspond, retourne [].
    # # """
    #     prompt = f"""
    # Tu es un assistant qui doit filtrer une liste de contacts Odoo selon cette requête utilisateur
    # Retourne uniquement les contacts pertinents en JSON (garde tous leurs champs).
    # Si aucun ne correspond, retourne [].
    # """
    #     response = query_deepseek(prompt)
    #     try:
    #         return json.loads(response)
    #     except:
    #         return []

