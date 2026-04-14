from pydantic import BaseModel, Field

class LoanApplicationRequest(BaseModel):
    aadhar_number: str = Field(..., min_length=12, max_length=12)
    pan_number: str
    company: str
    experience_years: int


class LoanDecisionResponse(BaseModel):
    applicant_name: str
    credit_score: int
    monthly_income: int
    existing_loans: int
    risk_score: int
    decision: str
