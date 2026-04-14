import csv

def generate_csv_report(data, filename="loan_decision_report.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data.keys())
        writer.writerow(data.values())
