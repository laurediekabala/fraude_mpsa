# services/decision_service.py

def decision_rule(probability: float, t_accept: float, t_review: float) -> str:
    """
    Règle de décision métier basée sur la probabilité de fraude.

    Args:
        probability (float): Probabilité de fraude [0,1]
        t_accept (float): seuil ACCEPT
        t_review (float): seuil REVIEW

    Returns:
        str: ACCEPT | REVIEW | REJECT
    """

    # Sécurité (production)
    probability = float(probability)
    probability = min(max(probability, 0.0), 1.0)

    if probability < t_accept:
        return "ACCEPT"
    elif probability < t_review:
        return "REVIEW"
    else:
        return "REJECT"