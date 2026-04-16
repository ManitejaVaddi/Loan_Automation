def clean_applicant_data(data: dict) -> dict:
    cleaned = {}

    for key, value in data.items():

        #  Handle None values smartly
        if value is None:
            if key in ["existing_loans", "experience_years"]:
                cleaned[key] = 0
            else:
                cleaned[key] = value
            continue

        #  Normalize numeric fields
        if key == "credit_score":
            cleaned[key] = int(value)

        elif key in ["monthly_income", "loan_amount"]:
            cleaned[key] = float(value)

        elif key in ["existing_loans", "experience_years"]:
            cleaned[key] = int(value)

        #  Clean strings
        elif isinstance(value, str):
            cleaned[key] = value.strip()

        else:
            cleaned[key] = value

    return cleaned