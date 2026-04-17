from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from pathlib import Path

from api.schemas import LoanApplicationRequest, LoanDecisionResponse
from main import process_loan_application
from storage.db import fetch_all_decisions

from auth.login import router as login_router
from auth.register import router as register_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Automated Loan Approval System",
    description="Internal API for automated loan eligibility, verification, and decisioning",
    version="1.0.0",
    docs_url=None,
    redoc_url="/redoc"
)

#  Auth Routes
app.include_router(login_router, prefix="/auth", tags=["Auth"])
app.include_router(register_router, prefix="/auth", tags=["Auth"])

#  Static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


#  Swagger UI
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Loan Automation API Docs",
        swagger_css_url="/static/swagger.css"
    )


#  Loan Apply API (FIXED)
@app.post("/loan/apply", response_model=LoanDecisionResponse, tags=["Loan Processing"])
def apply_loan(request: LoanApplicationRequest):
    """
    TEMP: user_id=1
    Later: replace with logged-in user
    """

    result = process_loan_application(
        user_id=1,   #  IMPORTANT (temporary fix)
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


# Audit endpoint
@app.get("/loan/audit", tags=["Audit"])
def audit_loans():
    return fetch_all_decisions()


#  Default route → Login Page ONLY (FIXED)
@app.get("/", include_in_schema=False)
def serve_login():
    return FileResponse(BASE_DIR / "static" / "login.html")