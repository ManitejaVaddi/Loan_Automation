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
            interest_rate REAL,
            review_status TEXT DEFAULT 'AUTO_DECIDED',
            final_decision TEXT,
            reviewer_notes TEXT,
            reviewed_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(loans)")
    columns = [row[1] for row in cursor.fetchall()]

    if "created_at" not in columns:
        cursor.execute("ALTER TABLE loans ADD COLUMN created_at TEXT")
    if "review_status" not in columns:
        cursor.execute("ALTER TABLE loans ADD COLUMN review_status TEXT DEFAULT 'AUTO_DECIDED'")
    if "final_decision" not in columns:
        cursor.execute("ALTER TABLE loans ADD COLUMN final_decision TEXT")
    if "reviewer_notes" not in columns:
        cursor.execute("ALTER TABLE loans ADD COLUMN reviewer_notes TEXT")
    if "reviewed_at" not in columns:
        cursor.execute("ALTER TABLE loans ADD COLUMN reviewed_at TEXT")

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
        interest_rate,
        review_status,
        final_decision,
        reviewer_notes,
        reviewed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    data["interest_rate"],
    "PENDING_REVIEW" if data["decision"] == "REVIEW" else "AUTO_DECIDED",
    data["decision"],
    None,
    None
))

    conn.commit()
    conn.close()


#  Fetch user loan history
def get_loans_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            applicant_name,
            credit_score,
            monthly_income,
            existing_loans,
            experience_years,
            loan_amount,
            risk_score,
            decision,
            loan_ratio,
            interest_rate,
            review_status,
            final_decision,
            reviewer_notes,
            reviewed_at,
            created_at
        FROM loans
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_review_queue():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
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
            interest_rate,
            review_status,
            final_decision,
            reviewer_notes,
            reviewed_at,
            created_at
        FROM loans
        WHERE decision = 'REVIEW' OR review_status != 'AUTO_DECIDED'
        ORDER BY
            CASE review_status
                WHEN 'PENDING_REVIEW' THEN 0
                ELSE 1
            END,
            id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_review_decision(loan_id, final_decision, reviewer_notes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE loans
        SET
            review_status = 'REVIEW_COMPLETED',
            final_decision = ?,
            reviewer_notes = ?,
            reviewed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (final_decision, reviewer_notes, loan_id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0


def get_review_analytics():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM loans")
    total_applications = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM loans WHERE final_decision = 'APPROVED'")
    approved_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM loans WHERE final_decision = 'REJECTED'")
    rejected_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM loans WHERE review_status = 'PENDING_REVIEW'")
    pending_review_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM loans WHERE review_status = 'REVIEW_COMPLETED'")
    completed_review_count = cursor.fetchone()[0]

    cursor.execute("SELECT ROUND(AVG(risk_score), 1) FROM loans")
    avg_risk_score = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ROUND(AVG((julianday(reviewed_at) - julianday(created_at)) * 24), 1)
        FROM loans
        WHERE reviewed_at IS NOT NULL AND created_at IS NOT NULL
    """)
    avg_review_turnaround_hours = cursor.fetchone()[0]

    conn.close()

    approval_rate = round((approved_count / total_applications) * 100, 1) if total_applications else 0

    return {
        "total_applications": total_applications,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "pending_review_count": pending_review_count,
        "completed_review_count": completed_review_count,
        "approval_rate": approval_rate,
        "avg_risk_score": avg_risk_score or 0,
        "avg_review_turnaround_hours": avg_review_turnaround_hours or 0
    }
