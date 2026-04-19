import hashlib
import re


def fetch_credit_score(pan_number: str) -> dict:
    
    #  Invalid PAN
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pattern, pan_number):
        return {
            "pan": pan_number,
            "credit_score": 500,
            "existing_loans": 3
        }

    #  Generate stable simulated profile for the same PAN
    digest = hashlib.sha256(pan_number.encode("utf-8")).hexdigest()
    profile_seed = int(digest[:8], 16)
    credit_score = 650 + (profile_seed % 151)
    existing_loans = (profile_seed // 151) % 3

    return {
        "pan": pan_number,
        "credit_score": credit_score,
        "existing_loans": existing_loans
    }
