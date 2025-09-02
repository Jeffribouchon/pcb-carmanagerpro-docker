from flask import Flask, render_template, request
import requests
from datetime import datetime
from modules.odoo.odoo_model import OdooModel
import base64

app = Flask(__name__)

API_URL = "https://openapi.fr/produits/verification-plaques-france"
odoo = OdooModel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    vehicle_data = []
    if request.method == 'POST':
        plates = request.form['plates']
        plate_list = [p.strip() for p in plates.split(',') if p.strip()]

        for plate in plate_list:
            vehicle_entry = {'plate': plate}
            # 🔹 Récupération des infos du véhicule via API
            response = requests.get(f"{API_URL}?plate={plate}")
            if response.status_code == 200:
                vehicle = response.json()
                vehicle_entry.update(vehicle)
                
                # 🔹 Vérification dans Odoo
                domain = [('default_code', '=', plate)]
                existing = odoo.search('product.product', domain)

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

                    odoo.create('product.product', product_vals)
                    vehicle_entry['odoo_status'] = 'Créé'
                    vehicle_entry['odoo_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                vehicle_entry['error'] = 'Impossible de récupérer les infos'

            vehicle_data.append(vehicle_entry)

    return render_template('vehicles.html', vehicle_data=vehicle_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
