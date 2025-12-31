def decision_rule(p, t_accept, t_reject):
    if p < t_accept:
        return "ACCEPT"
    elif p < t_reject:
        return "REVIEW"
    else:
        return "REJECT"
