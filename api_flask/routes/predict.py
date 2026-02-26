# routes/predict.py

from flask import Blueprint, request, jsonify
from services.prediction_service import predict_instance
from services.decision_service import decision_rule
from services.cost_service import compute_cost
import yaml
import os

predict_bp = Blueprint("predict", __name__)

config_path = os.path.join(os.path.dirname(__file__), "..", "config", "business.yaml")
with open(config_path, "r") as f:
    business = yaml.safe_load(f)

@predict_bp.route("", methods=["POST"])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "JSON vide"}), 400

        # -------------------------
        # Probabilité
        # -------------------------
        p = float(predict_instance(data))
        p = min(max(p, 0.0), 1.0)

        # -------------------------
        # Décision métier
        # -------------------------
        decision = decision_rule(
            p,
            business["thresholds"]["accept"],
            business["thresholds"]["review"]
        )

        # -------------------------
        # Coût attendu
        # -------------------------
        amount = data.get("amount", 0.0)
        cost = compute_cost(
            decision,
            business["costs"],
            probability=p,
            amount=amount
        )

        return jsonify({
            "probability": p,
            "decision": decision,
            "estimated_cost": round(cost, 6)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500