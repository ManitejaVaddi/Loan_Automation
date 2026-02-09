from ingestion.identity_api import verify_identity
from ingestion.employment_api import verify_employment
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
    company: str,
    experience_years: int
) -> dict:
    """
    End-to-end loan processing pipeline.
    Can be triggered via CLI, scheduler, or FastAPI.
    """

    try:
        logger.info("Starting loan application processing")

        # Ensure DB schema exists
        create_tables()

        # Step 1: Background Verification
        identity = verify_identity(aadhar_number)
        if not identity.get("verified"):
            logger.warning("Identity verification failed")
            return {"status": "FAILED", "reason": "Identity verification failed"}

        employment = verify_employment(company, experience_years)
        if not employment.get("verified"):
            logger.warning("Employment verification failed")
            return {"status": "FAILED", "reason": "Employment verification failed"}

        credit = fetch_credit_score(pan_number)

        # Step 2: Build applicant record
        applicant = {
            "name": identity.get("name"),
            "credit_score": credit.get("credit_score"),
            "monthly_income": employment.get("monthly_income"),
            "existing_loans": credit.get("existing_loans")
        }

        logger.info("Applicant data collected successfully")

        # Step 3: Data Cleaning & Validation
        cleaned = clean_applicant_data(applicant)

        if not validate_applicant(cleaned):
            logger.error("Applicant data validation failed")
            return {"status": "FAILED", "reason": "Invalid applicant data"}

        # Step 4: Risk Scoring
        risk_score = calculate_risk_score(
            cleaned["credit_score"],
            cleaned["monthly_income"],
            cleaned["existing_loans"]
        )

        decision = loan_decision(risk_score)

        # Step 5: Persist & Report
        cleaned.update({
            "risk_score": risk_score,
            "decision": decision
        })

        insert_decision(cleaned)
        generate_csv_report(cleaned)

        logger.info(
            f"Loan processed successfully | Applicant={cleaned['name']} | Decision={decision}"
        )

        return {
            "status": "SUCCESS",
            "applicant_name": cleaned["name"],
            "credit_score": cleaned["credit_score"],
            "monthly_income": cleaned["monthly_income"],
            "existing_loans": cleaned["existing_loans"],
            "risk_score": risk_score,
            "decision": decision
        }

    except Exception as exc:
        logger.exception("Unexpected error during loan processing")
        return {
            "status": "ERROR",
            "message": "Internal system error"
        }


if __name__ == "__main__":
    # Sample execution (CLI / testing)
    result = process_loan_application(
        aadhar_number="123456789012",
        pan_number="ABCDE1234F",
        company="TechCorp",
        experience_years=3
    )

    print(result)
