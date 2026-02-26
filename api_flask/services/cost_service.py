# services/cost_service.py

def compute_cost(decision, costs, probability=None, amount=None):
    """
    Calcule le coût business attendu de la décision.

    Args:
        decision (str): ACCEPT | REVIEW | REJECT
        costs (dict): dictionnaire des coûts métier
        probability (float): probabilité de fraude [0,1]
        amount (float): montant de la transaction

    Returns:
        float: coût estimé
    """

    # Sécurité
    probability = float(probability) if probability is not None else 0.0
    probability = min(max(probability, 0.0), 1.0)

    amount = float(amount) if amount and amount > 0 else 0.0

    # Facteur de risque basé sur le montant
    amount_risk_factor = min(amount / 10_000, 2.0) if amount > 0 else 1.0

    # ==================================================
    # REJECT → risque de faux positif
    # ==================================================
    if decision == "REJECT":
        false_positive_risk = 1.0 - probability
        return costs["fp"] * false_positive_risk * amount_risk_factor

    # ==================================================
    # ACCEPT → risque de faux négatif
    # ==================================================
    if decision == "ACCEPT":
        false_negative_risk = probability
        return costs["fn"] * false_negative_risk * amount_risk_factor

    # ==================================================
    # REVIEW → coût fixe + risque résiduel
    # ==================================================
    if decision == "REVIEW":
        manual_review_cost = costs.get("manual_review", 5.0)
        residual_fraud_risk = probability * costs["fn"] * 0.3
        return (manual_review_cost + residual_fraud_risk) * amount_risk_factor

    return 0.0