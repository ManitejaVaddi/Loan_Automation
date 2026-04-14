import random

def verify_employment(company: str, experience_years: int) -> dict:
    if experience_years < 1:
        return {"verified": False, "reason": "Insufficient experience"}

    return {
        "verified": True,
        "company": company,
        "experience_years": experience_years,
        "monthly_income": random.randint(30000, 120000)
    }
