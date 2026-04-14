def validate_applicant(data: dict) -> bool:
    required_fields = [
        "credit_score",
        "monthly_income",
        "existing_loans"
    ]

    for field in required_fields:
        if field not in data:
            return False

    return True
