from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.schemas import (
    LoanApplicationRequest,
    LoanDecisionResponse,
    LoanReviewDecisionRequest,
    LoanSimulationRequest,
)
from auth.login import router as login_router
from auth.register import router as register_router
from main import process_loan_application
from scoring.risk_engine import build_loan_assessment
from storage.db import fetch_all_decisions
from storage.loan_db import (
    create_loan_table,
    get_loans_by_user,
    get_review_analytics,
    get_review_queue,
    update_review_decision,
)
from storage.user_db import get_user_by_session

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Automated Loan Approval System",
    description="Internal API for automated loan eligibility, verification, and decisioning",
    version="1.0.0",
    docs_url=None,
    redoc_url="/redoc"
)

app.include_router(login_router, prefix="/auth", tags=["Auth"])
app.include_router(register_router, prefix="/auth", tags=["Auth"])
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def get_authenticated_user(x_session_token: str | None):
    if not x_session_token:
        raise HTTPException(status_code=401, detail="Login required")

    user = get_user_by_session(x_session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user session")

    return user


def require_reviewer_access(user):
    if user[3] not in {"admin", "reviewer"}:
        raise HTTPException(status_code=403, detail="Reviewer access required")
    return user


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Loan Automation API Docs",
        swagger_css_url="/static/swagger.css"
    )


@app.post("/loan/apply", response_model=LoanDecisionResponse, tags=["Loan Processing"])
def apply_loan(
    request: LoanApplicationRequest,
    x_session_token: str | None = Header(default=None)
):
    user = get_authenticated_user(x_session_token)

    result = process_loan_application(
        user_id=user[0],
        aadhar_number=request.aadhar_number,
        pan_number=request.pan_number,
        monthly_income=request.monthly_income,
        experience_years=request.experience_years,
        loan_amount=request.loan_amount
    )

    if result["status"] == "FAILED":
        raise HTTPException(status_code=400, detail=result["reason"])

    if result["status"] == "ERROR":
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@app.post("/loan/simulate", tags=["Loan Processing"])
def simulate_loan(
    request: LoanSimulationRequest,
    x_session_token: str | None = Header(default=None)
):
    get_authenticated_user(x_session_token)

    assessment = build_loan_assessment(
        request.credit_score,
        request.monthly_income,
        request.existing_loans,
        request.experience_years,
        request.loan_amount
    )

    return {
        "credit_score": request.credit_score,
        "monthly_income": request.monthly_income,
        "existing_loans": request.existing_loans,
        "experience_years": request.experience_years,
        "loan_amount": request.loan_amount,
        **assessment
    }


@app.get("/loan/audit", tags=["Audit"])
def audit_loans():
    return fetch_all_decisions()


@app.get("/loan/history", tags=["Loan Processing"])
def loan_history(x_session_token: str | None = Header(default=None)):
    user = get_authenticated_user(x_session_token)
    create_loan_table()
    rows = get_loans_by_user(user[0])

    return {
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3]
        },
        "applications": [
            {
                "id": row[0],
                "applicant_name": row[1],
                "credit_score": row[2],
                "monthly_income": row[3],
                "existing_loans": row[4],
                "experience_years": row[5],
                "loan_amount": row[6],
                "risk_score": row[7],
                "decision": row[8],
                "loan_ratio": row[9],
                "interest_rate": row[10],
                "review_status": row[11],
                "final_decision": row[12],
                "reviewer_notes": row[13],
                "reviewed_at": row[14],
                "created_at": row[15]
            }
            for row in rows
        ]
    }


@app.get("/review/queue", tags=["Review Panel"])
def review_queue(x_session_token: str | None = Header(default=None)):
    user = get_authenticated_user(x_session_token)
    require_reviewer_access(user)
    create_loan_table()
    rows = get_review_queue()

    return {
        "cases": [
            {
                "id": row[0],
                "user_id": row[1],
                "applicant_name": row[2],
                "credit_score": row[3],
                "monthly_income": row[4],
                "existing_loans": row[5],
                "experience_years": row[6],
                "loan_amount": row[7],
                "risk_score": row[8],
                "decision": row[9],
                "loan_ratio": row[10],
                "interest_rate": row[11],
                "review_status": row[12],
                "final_decision": row[13],
                "reviewer_notes": row[14],
                "reviewed_at": row[15],
                "created_at": row[16]
            }
            for row in rows
        ]
    }


@app.post("/review/{loan_id}/decision", tags=["Review Panel"])
def review_decision(
    loan_id: int,
    request: LoanReviewDecisionRequest,
    x_session_token: str | None = Header(default=None)
):
    user = get_authenticated_user(x_session_token)
    require_reviewer_access(user)
    create_loan_table()

    if not update_review_decision(loan_id, request.final_decision, request.reviewer_notes):
        raise HTTPException(status_code=404, detail="Review case not found")

    return {"message": "Review decision saved successfully"}


@app.get("/review/analytics", tags=["Review Panel"])
def review_analytics(x_session_token: str | None = Header(default=None)):
    user = get_authenticated_user(x_session_token)
    require_reviewer_access(user)
    create_loan_table()
    return get_review_analytics()


@app.get("/", include_in_schema=False)
def serve_login():
    return FileResponse(BASE_DIR / "static" / "login.html")
