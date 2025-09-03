from flask import Blueprint, render_template, request, jsonify
from modules.agents.contact_agent import ContactAgent

bp = Blueprint("ai_contacts", __name__)
agent = ContactAgent()

@bp.route("/ai-contacts", methods=["GET"])
def ai_contacts_page():
    return render_template("ai_contacts.html")

@bp.route("/ai-contacts/search", methods=["POST"])
def ai_contacts_search():
    query = request.json.get("query", "")
    try:
        criteria, results = agent.search(query)
        return jsonify({
            "success": True,
            "criteria": criteria,
            "results": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
