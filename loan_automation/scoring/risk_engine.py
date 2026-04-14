def calculate_risk_score(credit_score, income, existing_loans):
    score = 0

    # Credit Score Logic
    if credit_score >= 750:
        score += 50
    elif credit_score >= 650:
        score += 30
    else:
        score += 10

    # Income Logic
    if income >= 80000:
        score += 30
    elif income >= 40000:
        score += 20
    else:
        score += 10

    # Existing Loans Penalty
    score -= existing_loans * 5

    return score


def loan_decision(score):
    if score >= 70:
        return "APPROVED"
    elif score >= 50:
        return "REVIEW"
    else:
        return "REJECTED"
