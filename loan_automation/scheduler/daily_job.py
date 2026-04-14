from main import process_loan_application

def run_daily_job():
    print("Running scheduled loan verification job...")
    process_loan_application()
