# System-to-System Data Reconciliation Engine

A lightweight data validation tool that identifies discrepancies between source and target data systems during migrations and ETL syncs.

## Version 1 Capabilities
- **Duplicate Key Detection:** Captures duplicate keys in source or target before record matching.
- **Bi-directional Reconciliation:** Detects missing records in target as well as unmapped/unexpected records in target.
- **Granular Mismatch Auditing:** Evaluates field-level disparities (amounts, dates, statuses).
- **Automated Exception Reporting:** Generates structured exception reports (`results/exceptions.csv`).

## Project Structure
```text
system-reconciliation/
├── data/
│   ├── source_orders.csv
│   └── target_orders.csv
├── src/
│   └── reconcile.py
├── results/
│   └── exceptions.csv
└── README.md

How to Run
Bash
python src/reconcile.py

---

## Architectural Expansion (What Comes Next)

Version 1 establishes core record matching logic on static flat files. Here are three directions to take this project next:

1. **Version 2 — Database Integration:** Swap local CSVs for SQLite/PostgreSQL connections using standard SQL queries or `SQLAlchemy` to reconcile live database tables.
2. **Data Cleaning & Schema Handling:** Add configurable dynamic threshold checks (e.g., allow floating-point currency differences up to $0.01 without triggering a mismatch).
3. **Automated CI/CD Integration:** Set up GitHub Actions to auto-run `reconcile.py` on commit and attach the exception report as a pipeline artifact.

<ElicitationsGroup message="Which architectural direction would you like to take next?">
  <Elicitation label="Migrate Version 1 to use SQLite databases instead of static CSVs" query="Let's upgrade this system reconciliation engine to Version 2 by replacing local CSV files with an SQLite database implementation."/>
  <Elicitation label="Add automated unit testing and a GitHub Actions workflow pipeline" query="Let's set up automated testing and a GitHub Actions pipeline to run reconciliation on push."/>
  <Elicitation label="Enhance reconciliation logic with float tolerance and fuzzy text matching" query="Let's enhance the Python reconciliation script to handle floating-point tolerances and fuzzy text matching."/>
</ElicitationsGroup>
