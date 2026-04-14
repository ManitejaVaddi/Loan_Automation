def clean_applicant_data(data: dict) -> dict:
    cleaned = {}

    for key, value in data.items():
        if value is None:
            cleaned[key] = 0
        else:
            cleaned[key] = value

    return cleaned
