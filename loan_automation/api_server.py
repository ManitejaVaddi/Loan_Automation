from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from pathlib import Path

from api.schemas import LoanApplicationRequest
from main import process_loan_application
from storage.db import fetch_all_decisions

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Automated Loan Approval System",
    description="Internal API for automated loan eligibility, verification, and decisioning",
    version="1.0.0",
    docs_url=None,
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Loan Automation API Docs",
        swagger_css_url="/static/swagger.css"
    )


@app.post("/loan/apply", tags=["Loan Processing"])
def apply_loan(request: LoanApplicationRequest):
    result = process_loan_application(
        aadhar_number=request.aadhar_number,
        pan_number=request.pan_number,
        company=request.company,
        experience_years=request.experience_years
    )

    if result["status"] in ["FAILED", "ERROR"]:
        raise HTTPException(status_code=400, detail=result)

    return result


@app.get("/loan/audit", tags=["Audit"])
def audit_loans():
    return fetch_all_decisions()


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")
