from flask import Blueprint, request, jsonify
from services.prediction_service import predict_instance
from services.decision_service import decision_rule
from services.cost_service import compute_cost
import yaml
import os

predict_bp = Blueprint("predict", __name__)

# Utiliser un chemin relatif au fichier courant
config_path = os.path.join(os.path.dirname(__file__), "..", "config", "business.yaml")
with open(config_path) as f:
    business = yaml.safe_load(f)

@predict_bp.route("", methods=["POST"])
def predict():
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Données JSON vides"}), 400

        p = predict_instance(data)
        decision = decision_rule(
            p,
            business["thresholds"]["accept"],
            business["thresholds"]["reject"]
        )

        # Passer la probabilité et le montant au service de coût pour dynamicité
        amount = data.get("amount", 0)
        cost = compute_cost(decision, business["costs"], probability=p, amount=amount)

        return jsonify({
            "probability": p,
            "decision": decision,
            "estimated_cost": cost
        })
    except Exception as e:
        print(f"❌ Erreur dans /predict : {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
