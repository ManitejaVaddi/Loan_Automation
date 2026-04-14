Automated Loan Approval System

A Python-based internal tool that automates bank loan eligibility checks by replacing traditional mediator-driven workflows with rule-based background verification, risk scoring, and decisioning.
The system is built with FastAPI, modular Python services, and a lightweight frontend for non-technical users.

📌 Project Overview

Traditional loan approval processes involve manual verification, third-party agents, and delays.
This project demonstrates how such workflows can be automated using Python by:

Verifying applicant background details

Applying deterministic risk rules

Generating loan decisions

Maintaining audit logs and reports

Exposing workflows via APIs and a simple frontend

The system is designed as an internal bank tool, not a public consumer application.

🧠 Key Features
🔹 Python Automation

Automated identity, employment, and credit verification (simulated APIs)

End-to-end loan processing pipeline

Rule-based risk scoring (APPROVED / REVIEW / REJECTED)

🔹 Backend (FastAPI)

REST APIs for loan application and audit retrieval

Input validation using Pydantic

Structured error handling

Modular, reusable service design

🔹 Data Engineering

Data cleaning and validation

SQLite-based persistence for auditability

CSV report generation for decisions

🔹 Frontend

Lightweight HTML, CSS, and JavaScript UI

No page reloads (AJAX-based interaction)

Displays loan decision and risk details in real time

Designed for internal stakeholders

🔹 Engineering Discipline

Logging with rotation

Environment-based configuration using .env

Clean project structure

Sensitive and generated files excluded via .gitignore

🏗️ Architecture Overview
Frontend (HTML/CSS/JS)
        ↓
FastAPI API Layer
        ↓
Python Automation Pipeline
        ↓
Verification → Risk Engine → Decision
        ↓
SQLite Storage + Logs + Reports

📁 Project Structure
loan_automation/
│
├── api/
│   └── schemas.py
│
├── ingestion/
│   ├── identity_api.py
│   ├── employment_api.py
│   └── credit_api.py
│
├── processing/
│   ├── cleaning.py
│   └── validation.py
│
├── scoring/
│   └── risk_engine.py
│
├── storage/
│   └── db.py
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── logs/
│
├── main.py
├── api_server.py
├── logger.py
├── .gitignore
└── README.md

⚙️ Tech Stack

Python 3

FastAPI

SQLite

HTML / CSS / JavaScript

Pydantic

python-dotenv

Git

▶️ How to Run the Project
1️⃣ Install dependencies
pip install fastapi uvicorn python-dotenv

2️⃣ Start the server