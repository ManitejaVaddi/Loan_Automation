import random
import re


def fetch_credit_score(pan_number: str) -> dict:
    
    # ❌ Invalid PAN
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pattern, pan_number):
        return {
            "pan": pan_number,
            "credit_score": 500,
            "existing_loans": 3
        }

    # ✅ Generate realistic credit profile
    credit_score = random.randint(650, 800)
    existing_loans = random.randint(0, 2)

    return {
        "pan": pan_number,
        "credit_score": credit_score,
        "existing_loans": existing_loans
    }