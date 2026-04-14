import random
import time

def verify_identity(aadhar_number: str) -> dict:
    time.sleep(0.5)  # simulate API latency

    if len(aadhar_number) != 12:
        return {"status": "failed", "reason": "Invalid Aadhaar length"}

    return {
        "status": "success",
        "name": "Sample User",
        "dob": "1999-06-12",
        "verified": random.choice([True, True, False])
    }
