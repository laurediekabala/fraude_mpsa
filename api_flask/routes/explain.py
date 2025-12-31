from flask import Blueprint, request, jsonify
from services.shap_service import explain_instance

explain_bp = Blueprint("explain", __name__)

@explain_bp.route("", methods=["POST"])
def explain():
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Données JSON vides"}), 400
            
        shap_values = explain_instance(data)
        return jsonify({"shap_values": shap_values})
    except Exception as e:
        print(f"❌ Erreur dans /explain : {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
