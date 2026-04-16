def verify_employment(company: str, experience_years: int) -> dict:
    
    #  Invalid input
    if not company or experience_years < 0:
        return {
            "verified": False,
            "reason": "Invalid employment data"
        }

    #  Fresher rule (optional business rule)
    if experience_years == 0:
        return {
            "verified": False,
            "reason": "No work experience"
        }

    #  Income calculation (realistic growth)
    base_salary = 30000
    increment_per_year = 5000

    monthly_income = base_salary + (experience_years * increment_per_year)

    return {
        "verified": True,
        "company": company.strip(),
        "experience_years": experience_years,
        "monthly_income": monthly_income
    }