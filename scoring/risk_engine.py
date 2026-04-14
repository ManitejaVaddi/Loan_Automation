def calculate_risk_score(credit_score, income, existing_loans, experience_years, loan_amount):
    score = 0
    reasons = []

    # ❌ Hard rejection rule
    if credit_score < 550:
        return 0, ["Very low credit score"]

    # ✅ Credit Score
    if credit_score >= 750:
        score += 40
    elif credit_score >= 650:
        score += 25
        reasons.append("Average credit score")
    else:
        score += 10
        reasons.append("Low credit score")

    # ✅ Income vs Loan Ratio
    ratio = loan_amount / income
    if ratio < 0.3:
        score += 30
    elif ratio < 0.6:
        score += 15
        reasons.append("Moderate loan burden")
    else:
        score += 5
        reasons.append("High loan burden")

    # ✅ Employment Stability
    if experience_years >= 3:
        score += 20
    elif experience_years >= 1:
        score += 10
        reasons.append("Moderate job stability")
    else:
        reasons.append("Unstable employment")

    # ✅ Existing Loans Penalty
    penalty = existing_loans * 5
    score -= penalty
    if existing_loans > 2:
        reasons.append("Too many existing loans")

    return score, reasons


def loan_decision(score):
    if score >= 70:
        return "APPROVED"
    elif score >= 40:
        return "REVIEW"
    else:
        return "REJECTED"