import sqlite3
from sqlite3 import Error
from logger import setup_logger

DB_NAME = "loan_system.db"
logger = setup_logger()


def get_connection():
    """
    Create and return a database connection.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except Error as e:
        logger.exception("Failed to connect to database")
        raise


def create_tables():
    """
    Create required tables if they do not exist.
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS loan_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    credit_score INTEGER NOT NULL,
                    income INTEGER NOT NULL,
                    loans INTEGER NOT NULL,
                    risk_score INTEGER NOT NULL,
                    decision TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

        logger.info("Database tables initialized successfully")

    except Exception:
        logger.exception("Error while creating database tables")
        raise


def insert_decision(data: dict):
    """
    Insert a loan decision record into the database.
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO loan_decisions
                (name, credit_score, income, loans, risk_score, decision)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["name"],
                data["credit_score"],
                data["monthly_income"],
                data["existing_loans"],
                data["risk_score"],
                data["decision"]
            ))
            conn.commit()

        logger.info(
            f"Loan decision stored | Applicant={data['name']} | Decision={data['decision']}"
        )

    except KeyError as e:
        logger.error(f"Missing required field while inserting decision: {e}")
        raise

    except Exception:
        logger.exception("Failed to insert loan decision into database")
        raise


def fetch_all_decisions():
    """
    Fetch all loan decisions for audit/reporting.
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    id,
                    name,
                    credit_score,
                    income,
                    loans,
                    risk_score,
                    decision,
                    created_at
                FROM loan_decisions
                ORDER BY created_at DESC
            """)
            rows = cur.fetchall()

        logger.info("Fetched all loan decisions for audit")
        return rows

    except Exception:
        logger.exception("Failed to fetch loan decisions")
        raise
