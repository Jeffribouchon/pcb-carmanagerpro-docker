from modules.odoo.odoo_model import OdooModel


# https://openapi.fr/produits/verification-plaques-france
API_URL = "https://automotive.openapi.com/FR-car"

class ImmatAgent(BaseAgent):
        
    def __init__(self, odoo_client):
        product_template = OdooModel(odoo_client, 'product.template')

    def search(self):
        plates = request.form['plates']
        plate_list = [p.strip() for p in plates.split(',') if p.strip()]

        for plate in plate_list:
            vehicle_entry = {'plate': plate}
            # 🔹 Récupération des infos du véhicule via API
            clean_plate = re.sub(r'[^A-Za-z0-9]', '', plate)
            response = requests.get(f"{API_URL}/{clean_plate}")
            
            if response.status_code == 200:
                vehicle = response.json()
                vehicle_entry.update(vehicle)
                
                # 🔹 Vérification dans Odoo
                domain = [('x_immatriculation', '=', plate)]
                existing = product_template.search(domain)

                if existing:
                    vehicle_entry['odoo_status'] = 'Existant'
                    vehicle_entry['odoo_date'] = None
                else:
                    # 🔹 Création produit
                    product_vals = {
                        'name': f"{vehicle.get('make','N/A')} {vehicle.get('model','N/A')}",
                        'default_code': plate,
                        'list_price': vehicle.get('price', 0),
                        'type': 'product',
                        'categ_id': 5,  # Catégorie véhicules
                        'description_sale': f"Énergie: {vehicle.get('fuel','N/A')}, Année: {vehicle.get('year','N/A')}",
                    }
                    # Ajouter l'image si disponible
                    if vehicle.get('image'):
                        image_data = requests.get(vehicle['image']).content
                        product_vals['image_1920'] = base64.b64encode(image_data).decode('utf-8')

                    product_template.create(product_vals)
                    vehicle_entry['odoo_status'] = 'Créé'
                    vehicle_entry['odoo_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                vehicle_entry['error'] = 'Impossible de récupérer les infos'

            return vehicle_data.append(vehicle_entry)
