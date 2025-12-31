def compute_cost(decision, costs, probability=None, amount=None):
    """
    Calcule le coût estimé basé sur la décision, la probabilité et le montant.
    
    Args:
        decision: La décision prise (ACCEPT, REVIEW, REJECT)
        costs: Dictionnaire avec les coûts FP et FN
        probability: Probabilité de fraude (0-1), optionnel
        amount: Montant de la transaction, optionnel
    
    Returns:
        Coût estimé en dollars
    """
    
    # Normaliser le montant (si > 10000, considérer comme transaction à haut risque)
    amount_risk_factor = 1.0
    if amount and amount > 0:
        # Plus le montant est élevé, plus le coût potentiel est grand
        amount_risk_factor = min(amount / 10000, 2.0)  # Max 2x pour les très gros montants
    
    if decision == "REJECT":
        # Coût de rejeter une transaction
        # Si probabilité basse = faux positif coûteux
        # Si probabilité haute = bonne décision (peu coûteuse)
        if probability is not None:
            # Risque que ce soit un vrai client (faux positif)
            false_positive_risk = (1 - probability)
            # Le coût dépend du montant rejeté
            return costs["fp"] * false_positive_risk * amount_risk_factor
        else:
            return costs["fp"] * amount_risk_factor
    
    elif decision == "ACCEPT":
        # Coût d'accepter une transaction
        # Si probabilité haute = on accepte une fraude probable
        if probability is not None:
            # Risque de fraude acceptée
            false_negative_risk = probability
            # Le coût dépend du montant accepté frauduleusement
            return costs["fn"] * false_negative_risk * amount_risk_factor
        else:
            return 0
    
    else:  # REVIEW
        # Coût de révision manuelle = coût intermédiaire
        if probability is not None:
            review_cost = costs["fn"] * 0.2 * probability * amount_risk_factor
            return review_cost
        else:
            return costs["fn"] * 0.1 * amount_risk_factor


