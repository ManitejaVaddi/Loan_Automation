import time


def verify_identity(aadhar_number: str) -> dict:
    time.sleep(0.3)  # simulate API latency

    #  Invalid Aadhaar
    if not aadhar_number.isdigit() or len(aadhar_number) != 12:
        return {
            "status": "failed",
            "reason": "Invalid Aadhaar format",
            "verified": False
        }

    #  Fake pattern (all digits same)
    if len(set(aadhar_number)) == 1:
        return {
            "status": "failed",
            "reason": "Suspicious Aadhaar number",
            "verified": False
        }

    #  Success
    return {
        "status": "success",
        "name": f"User_{aadhar_number[-4:]}",
        "dob": "1999-06-12",
        "verified": True
    }