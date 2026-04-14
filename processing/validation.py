def validate_applicant(data: dict) -> bool:
    required_fields = [
        "credit_score",
        "monthly_income",
        "existing_loans",
        "experience_years",
        "loan_amount"
    ]

    # ✅ Check missing fields
    for field in required_fields:
        if field not in data:
            return False

    # ✅ Type & value checks
    try:
        credit_score = int(data["credit_score"])
        income = float(data["monthly_income"])
        loans = int(data["existing_loans"])
        experience = int(data["experience_years"])
        loan_amount = float(data["loan_amount"])
    except (ValueError, TypeError):
        return False

    # ✅ Logical validations
    if not (300 <= credit_score <= 900):
        return False

    if income <= 0:
        return False

    if loan_amount <= 0:
        return False

    if loans < 0:
        return False

    if experience < 0:
        return False

    return True