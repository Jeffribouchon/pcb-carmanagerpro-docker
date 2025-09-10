from modules.agents.base_agent import BaseAgent

class ImmatAgent(BaseAgent):
    def __init__(self, odoo, deepseek):
        self.odoo = odoo
        self.deepseek = deepseek

    def parse_and_create_vehicle(self, raw_text: str):
        """
        Analyse un copier-coller Carter-Cash et crée un véhicule Odoo
        """
        # 1. Demander à DeepSeek d'extraire les infos structurées
        prompt = f"""
        Tu es un assistant spécialisé en parsing automobile. 
        Analyse le texte fourni et retourne UNIQUEMENT un JSON valide. 
        Pas de texte avant ou après, pas de commentaires.

        Champs attendus (si une info est manquante, retourne null) :
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
        - date_mec (string au format YYYY-MM-DD)
        - ktype (string)
        - numero_serie (string)

        Texte à analyser :
        \"\"\"{raw_text}\"\"\"
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
