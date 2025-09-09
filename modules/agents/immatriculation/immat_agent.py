from modules.odoo_client import OdooClient
from modules.agents.base import BaseAgent
from deepseek import DeepSeekClient  # ton wrapper DeepSeek

class CarterCashAgent(BaseAgent):
    def __init__(self, odoo: OdooClient, deepseek: DeepSeekClient):
        self.odoo = odoo
        self.deepseek = deepseek

    def parse_and_create_vehicle(self, raw_text: str):
        """
        Analyse un copier-coller Carter-Cash et crée un véhicule Odoo
        """
        # 1. Demander à DeepSeek d'extraire les infos structurées
        prompt = f"""
        Analyse ce texte et retourne un JSON avec les infos suivantes :
        marque, modele, version, carrosserie, vin, energie, moteur,
        couleur, immatriculation, puissance_cv, puissance_kw,
        boite_vitesse, type_propulsion, date_mec, ktype.
        
        Texte : {raw_text}
        """
        result = self.deepseek.extract_json(prompt)

        # 2. Mapper vers Odoo (product.template ou modèle véhicule)
        vehicle_data = {
            "name": f"{result.get('marque')} {result.get('modele')} {result.get('version')}",
            "x_vin": result.get("vin"),
            "x_immatriculation": result.get("immatriculation"),
            "x_motorisation": result.get("moteur"),
            "x_energie": result.get("energie"),
            "x_puissance_cv": result.get("puissance_cv"),
            "x_puissance_kw": result.get("puissance_kw"),
            "x_boite_vitesse": result.get("boite_vitesse"),
            "x_type_propulsion": result.get("type_propulsion"),
            "x_date_mec": result.get("date_mec"),
            "x_couleur": result.get("couleur"),
            "x_ktype": result.get("ktype"),
        }

        # 3. Créer dans Odoo
        vehicle_id = self.odoo.create("product.template", vehicle_data)
        return vehicle_id, vehicle_data
