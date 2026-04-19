from pydantic import BaseModel, Field, field_validator
import re


class LoanApplicationRequest(BaseModel):
    aadhar_number: str = Field(..., min_length=12, max_length=12)
    pan_number: str
    monthly_income: float = Field(..., gt=0)
    experience_years: int = Field(..., ge=0)
    loan_amount: float = Field(..., gt=0)  
    #  PAN format validation
    @field_validator("pan_number")
    @classmethod
    def validate_pan(cls, v):
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid PAN format")
        return v

    #  Aadhaar numeric check
    @field_validator("aadhar_number")
    @classmethod
    def validate_aadhar(cls, v):
        if not v.isdigit():
            raise ValueError("Aadhaar must be numeric")
        return v


class LoanDecisionResponse(BaseModel):
    status: str
    applicant_name: str
    credit_score: int
    monthly_income: float
    existing_loans: int
    experience_years: int
    loan_amount: float
    risk_score: int
    decision: str
    loan_ratio: float
    interest_rate: float
    reasons: list[str]
    improvement_suggestions: list[str]


class LoanSimulationRequest(BaseModel):
    credit_score: int = Field(..., ge=300, le=900)
    monthly_income: float = Field(..., gt=0)
    existing_loans: int = Field(..., ge=0)
    experience_years: int = Field(..., ge=0)
    loan_amount: float = Field(..., gt=0)


class LoanReviewDecisionRequest(BaseModel):
    final_decision: str
    reviewer_notes: str = Field(..., min_length=5, max_length=500)

    @field_validator("final_decision")
    @classmethod
    def validate_final_decision(cls, v):
        if v not in {"APPROVED", "REJECTED"}:
            raise ValueError("Final decision must be APPROVED or REJECTED")
        return v
