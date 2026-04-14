import random

def fetch_credit_score(pan_number: str) -> dict:
    return {
        "pan": pan_number,
        "credit_score": random.randint(550, 850),
        "existing_loans": random.randint(0, 3)
    }
