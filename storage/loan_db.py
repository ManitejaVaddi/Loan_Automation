import sqlite3

DB_NAME = "loan.db"


#  Create loan table
def create_loan_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            applicant_name TEXT,
            credit_score INTEGER,
            monthly_income REAL,
            existing_loans INTEGER,
            experience_years INTEGER,
            loan_amount REAL,
            risk_score INTEGER,
            decision TEXT,
            loan_ratio REAL,
            interest_rate REAL
        )
    """)

    conn.commit()
    conn.close()


#  Insert loan record
def insert_loan(user_id, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO loans (
            user_id,
            applicant_name,
            credit_score,
            monthly_income,
            existing_loans,
            experience_years,
            loan_amount,
            risk_score,
            decision,
            loan_ratio,
            interest_rate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data["applicant_name"],
        data["credit_score"],
        data["monthly_income"],
        data["existing_loans"],
        data["experience_years"],
        data["loan_amount"],
        data["risk_score"],
        data["decision"],
        data["loan_ratio"],
        data["interest_rate"]
    ))

    conn.commit()
    conn.close()


#  Fetch user loan history
def get_loans_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT applicant_name, loan_amount, decision, risk_score
        FROM loans
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows