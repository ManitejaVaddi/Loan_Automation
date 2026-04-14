from ingestion.identity_api import verify_identity
from ingestion.credit_api import fetch_credit_score

from processing.cleaning import clean_applicant_data
from processing.validation import validate_applicant

from scoring.risk_engine import calculate_risk_score, loan_decision
from storage.db import create_tables, insert_decision
from reporting.decision_report import generate_csv_report

from logger import setup_logger

logger = setup_logger()


def process_loan_application(
    aadhar_number: str,
    pan_number: str,
    experience_years: int,
    loan_amount: float,
    monthly_income: float   # ✅ NEW
) -> dict:

    try:
        logger.info("Starting loan application processing")

        # ✅ DB setup
        create_tables()

        # 🔹 Step 1: Identity Verification
        identity = verify_identity(aadhar_number)
        print("IDENTITY:", identity)

        if not identity.get("verified"):
            return {"status": "FAILED", "reason": "Identity verification failed"}

        # 🔹 Step 2: Credit Fetch
        credit = fetch_credit_score(pan_number)
        print("CREDIT:", credit)

        # 🔹 Step 3: Build Applicant (FIXED)
        applicant = {
            "name": identity.get("name"),
            "credit_score": credit.get("credit_score"),
            "monthly_income": monthly_income,   # ✅ from user
            "existing_loans": credit.get("existing_loans"),
            "experience_years": experience_years,
            "loan_amount": loan_amount
        }

        print("APPLICANT:", applicant)

        # 🔹 Step 4: Cleaning & Validation
        cleaned = clean_applicant_data(applicant)
        print("CLEANED:", cleaned)

        if not validate_applicant(cleaned):
            return {"status": "FAILED", "reason": "Invalid applicant data"}

        # 🔹 Step 5: Risk Calculation
        risk_score, reasons = calculate_risk_score(
            cleaned["credit_score"],
            cleaned["monthly_income"],
            cleaned["existing_loans"],
            cleaned["experience_years"],
            cleaned["loan_amount"]
        )

        decision = loan_decision(risk_score)

        # 🔹 Step 6: Save & Report
        cleaned.update({
            "risk_score": risk_score,
            "decision": decision
        })

        insert_decision(cleaned)
        generate_csv_report(cleaned)

        logger.info(f"Loan processed | {cleaned['name']} → {decision}")

        return {
            "status": "SUCCESS",
            "applicant_name": cleaned["name"],
            "credit_score": cleaned["credit_score"],
            "monthly_income": cleaned["monthly_income"],
            "existing_loans": cleaned["existing_loans"],
            "experience_years": cleaned["experience_years"],
            "loan_amount": cleaned["loan_amount"],
            "risk_score": risk_score,
            "decision": decision,
            "reasons": reasons
        }

    except Exception as exc:
        print("ERROR:", str(exc))
        logger.exception("Processing error")
        return {
            "status": "ERROR",
            "message": str(exc)
        }


# ✅ CLI test
if __name__ == "__main__":
    result = process_loan_application(
        aadhar_number="123456789012",
        pan_number="ABCDE1234F",
        experience_years=3,
        loan_amount=200000,
        monthly_income=50000   # ✅ REQUIRED NOW
    )

    print(result)