import re
import json
from modules.agents.base_agent import BaseAgent
from modules.odoo.odoo_model import OdooModel
from modules.utils.deepseek_client  import DeepSeekClient 

CRITERIA_PROMPT = """
Tu es un assistant spécialisé en parsing automobile. 
Analyse le texte fourni et retourne UNIQUEMENT un JSON valide. 
Pas de texte avant ou après, pas de commentaires.

Champs attendus (si une info est manquante, retourne null) :
- type_vehicule (string)
- marque (string)
- modele (string)
- version (string)
- carrosserie (string)
- genre (string)
- nb_portes (int)
- vin (string)
- energie (string)
- moteur (string)
- couleur (string)
- immatriculation (string)
- puissance_cv (int)
- puissance_kw (int)
- turbo (string)
- boite_vitesse (string)
- type_propulsion (string)
- date_mec (string au format YYYY)
- ktype (string)
- numero_serie (string)

⚠️ RÈGLES IMPORTANTES :
- Pour `boite_vitesse`, renvoie uniquement "Manuelle" ou "Automatique".
- Pour `energie`, renvoie uniquement "Diesel" ou "Essence" ou "Hybride" ou "Electrique" ou "GPL".
- Pour `marque`, renvoie tout en majuscule.
- Pour `modèle`, renvoie avec seulement la première lettre en majuscule.
- Pour `couleur`, renvoie avec seulement la première lettre en majuscule.
- Pour 'type_vehicule', renvoie une des codes suivants : 
        CITADINE pour Citadine	
        COMPACT	pour Compacte	
        BERLINE	pour Berline	
        FAMBRK	pour Breaks familiaux	
        SUVFAM	pour SUV Familiaux	
        SUVCMP	pour SUV Compact	
        MONOSPC	pour Monospaces	
        FOURX4	pour 4x4	
        UTILITE	pour Utilitaire léger	
        COUPE	pour Coupé	
        CABRIOLET pour	Cabriolet	
        ELECHYB	pour Véhicules électriques / hybrides	
        SOCVEHI	pour Véhicule de société	
        PREMIUM	pour Véhicule premium	
        LUXSPORT pour Véhicule de luxe / sport
- Si une valeur n’est pas présente, mets `null`.
- Retourne uniquement l’objet JSON, sans texte supplémentaire.
"""

class ImmatAgent(BaseAgent):
        
    def __init__(self, odoo_client):
        self.product_template = OdooModel(odoo_client, 'product.template')

    def extract_criteria(self, query: str) -> dict:
        """Utilise DeepSeek pour transformer une requête texte en critères structurés."""
        response = DeepSeekClient(CRITERIA_PROMPT, query)

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
            
    def search(self, criteria: str):
        """
        Analyse un copier-coller Carter-Cash et crée un véhicule Odoo
        """
        # 1. Mapper vers Odoo (product.template ou modèle véhicule)
        marque = criteria.get('marque')
        if marque:
            marque = " ".join(word.capitalize() for word in marque.split())
        
        vehicle_data = {
            "categ_id": 5,
            "name": f"{criteria.get('marque')} {criteria.get('modele')} {criteria.get('version')}",
            "x_studio_type_de_vhicule": criteria.get('type_vehicule'),
            "x_studio_marque": marque,
            "x_studio_modele": criteria.get('modele'),
            "x_etat_vehicule": "Roulant",
            "x_immatriculation": criteria.get('immatriculation'),
            "x_numero_chassis": criteria.get('vin'),
            "x_studio_boite_de_vitesse": criteria.get('boite_vitesse'),
            "x_studio_couleur": criteria.get('couleur'),
            "x_puissance_din_int": criteria.get('puissance_cv'),
            "x_studio_anne_de_mise_en_circulation": criteria.get('date_mec'),
            "x_studio_energie": criteria.get('energie'),
            "is_storable": True,
        }
        #     "qty_available": 1,

        # 2. Créer dans Odoo
        vehicle_id = self.product_template.create(vehicle_data)
        return vehicle_id, vehicle_data
