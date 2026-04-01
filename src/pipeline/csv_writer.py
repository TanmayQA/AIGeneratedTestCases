import csv

CSV_COLUMNS = [
    "Requirement_ID",
    "TC_ID",
    "Scenario",
    "Pre-Conditions",
    "Steps",
    "Test Data",
    "Expected Result",
    "Priority",
    "Type",
    "Tags",
    "Execution Team",
    "Automation Candidate",
]


def write_csv_output(data: list, filepath: str):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_COLUMNS,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()

        for row in data:
            normalized = {col: str(row.get(col, "")).strip() for col in CSV_COLUMNS}
            writer.writerow(normalized)
