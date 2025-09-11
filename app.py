from flask import Flask, render_template, request
import re
import requests
import base64
from datetime import datetime
from modules.odoo.client import OdooClient

from modules.agents.contacts.contact_agent import ContactAgent
from modules.agents.contacts.cleanup_agent import CleanupAgent
from modules.agents.matching.matching_agent import MatchingAgent
from modules.agents.immatriculation.immat_agent import ImmatAgent
from modules.agents.vehicles.generate_url_agent import GenerateUrlAgent

app = Flask(__name__)

odoo_client = OdooClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    vehicle_data = []
    # if request.method == 'POST':


    return render_template('vehicles.html', vehicle_data=vehicle_data)


# --- PAGE DEEPSEEK CONTACTS ---
@app.route("/ai-contacts", methods=["GET", "POST"])
def ai_contacts():
    results = None
    extracted_criteria = None

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            agent = ContactAgent(odoo_client)
            extracted_criteria = agent.extract_criteria(query)
            results = agent.search(extracted_criteria)

    return render_template("ai_contacts.html", results=results, criteria=extracted_criteria)


@app.route("/cleanup")
def cleanup():
    agent = CleanupAgent()
    results = agent.search()

    return render_template("cleanup.html", results=results)


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


@app.route("/immat_import", methods=["GET", "POST"])
def immat_import():
    existing_vehicle = None
    vehicle_id = None
    results = None
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            agent = ImmatAgent(odoo_client)
            extracted_criteria = agent.extract_criteria(query)
            existing_vehicle, vehicle_id, vehicle_data = agent.search(extracted_criteria)
            results = vehicle_data

    return render_template("immat_import.html", existing_vehicle=existing_vehicle, vehicle_id=vehicle_id, vehicle=results)


# --- PAGE DEEPSEEK GENERATEUR D'URL ---
@app.route("/generate_url", methods=["GET", "POST"])
def generate_url():
    results = None
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            agent = GenerateUrlAgent()
            extracted_criteria = agent.extract_criteria(query)
            results, lbc_results = agent.search(extracted_criteria)

    return render_template("generate_url.html", results=results, lbc_results=lbc_results)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
