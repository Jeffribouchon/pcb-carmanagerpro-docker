from flask import Flask, render_template, request
import re
import requests
from datetime import datetime
from modules.odoo.client import OdooClient
from modules.utils.deepseek_client import DeepSeekClient

from modules.odoo.odoo_model import OdooModel
from modules.agents.contacts.contact_agent import ContactAgent
from modules.agents.contacts.cleanup_agent import CleanupAgent
from modules.agents.matching.matching_agent import MatchingAgent
from modules.agents.immatriculation.immat_agent import ImmatAgent
import base64

app = Flask(__name__)

# https://openapi.fr/produits/verification-plaques-france
API_URL = "https://automotive.openapi.com/FR-car"
odoo_client = OdooClient()
deepseek_client = DeepSeekClient
product_template = OdooModel(odoo_client, 'product.template')

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

            vehicle_data.append(vehicle_entry)

    return render_template('vehicles.html', vehicle_data=vehicle_data)

# --- PAGE DEEPSEEK CONTACTS ---
@app.route("/ai-contacts", methods=["GET", "POST"])
def ai_contacts():
    results = None
    extracted_criteria = None

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            agent = ContactAgent()
            extracted_criteria = agent.extract_criteria(query)
            results = agent.search(extracted_criteria)

    return render_template("ai_contacts.html", results=results, criteria=extracted_criteria)

@app.route("/cleanup")
def cleanup():
    agent = CleanupAgent()
    results = agent.search()

    return render_template("cleanup.html", results=results)

@app.route("/immat_import", methods=["GET", "POST"])
def immat_import():
    vehicle = None
    if request.method == "POST":
        query = request.form.get("immat_text")
        if query:
            agent = ImmatAgent(odoo_client, deepseek_client)
            extracted_criteria = agent.extract_criteria(query)
            vehicle_id, vehicle_data = agent.parse_and_create_vehicle(extracted_criteria)
            vehicle = vehicle_data

    return render_template("immat_import.html", vehicle=vehicle)


@app.route("/matching", methods=["GET", "POST"])
def matching():
    contacts = []
    query = None
    extracted_criteria = None

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            agent = MatchingAgent()
            # 🔹 Passe le query au MatchingAgent
            extracted_criteria = agent.extract_criteria(query)
            contacts = agent.search(extracted_criteria)

    return render_template("matching.html", contacts=contacts, query=query)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
