import csv
from collections import defaultdict

# Path configuration
SOURCE_FILE = 'data/source_orders.csv'
TARGET_FILE = 'data/target_orders.csv'
REPORT_FILE = 'results/exceptions.csv'

# Fields to evaluate for value mismatches
CHECK_FIELDS = ['Customer_ID', 'Order_Date', 'Order_Amount', 'Order_Status', 'Currency']


def load_dataset(file_path):
    """
    Reads CSV and structures data into a dictionary for O(1) key lookups.
    Tracks duplicate primary keys to prevent silent data overwrites.
    """
    records = {}
    duplicates = []

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['Order_ID']
            if order_id in records:
                duplicates.append(row)
            else:
                records[order_id] = row

    return records, duplicates


def run_reconciliation():
    source_records, source_dups = load_dataset(SOURCE_FILE)
    target_records, target_dups = load_dataset(TARGET_FILE)

    exceptions = []

    # -------------------------------------------------------------
    # 1. RULE: Identify Duplicate Primary Keys in Source & Target
    # -------------------------------------------------------------
    for dup in source_dups:
        exceptions.append({
            'Order_ID': dup['Order_ID'],
            'Issue': 'Duplicate Record in Source',
            'Field': 'Order_ID',
            'Source_Value': dup['Order_ID'],
            'Target_Value': 'N/A'
        })

    for dup in target_dups:
        exceptions.append({
            'Order_ID': dup['Order_ID'],
            'Issue': 'Duplicate Record in Target',
            'Field': 'Order_ID',
            'Source_Value': 'N/A',
            'Target_Value': dup['Order_ID']
        })

    # -------------------------------------------------------------
    # 2. RULE: Compare Source against Target
    # -------------------------------------------------------------
    for order_id, src_row in source_records.items():
        if order_id not in target_records:
            # Record failed to migrate
            exceptions.append({
                'Order_ID': order_id,
                'Issue': 'Missing in Target',
                'Field': 'Order_ID',
                'Source_Value': order_id,
                'Target_Value': 'MISSING'
            })
        else:
            tgt_row = target_records[order_id]
            # Check individual fields for discrepancies
            for field in CHECK_FIELDS:
                if src_row[field] != tgt_row[field]:
                    exceptions.append({
                        'Order_ID': order_id,
                        'Issue': f'Value Mismatch ({field})',
                        'Field': field,
                        'Source_Value': src_row[field],
                        'Target_Value': tgt_row[field]
                    })

    # -------------------------------------------------------------
    # 3. RULE: Identify Unexpected / Extra Records in Target
    # -------------------------------------------------------------
    for order_id in target_records:
        if order_id not in source_records:
            exceptions.append({
                'Order_ID': order_id,
                'Issue': 'Unexpected Record in Target',
                'Field': 'Order_ID',
                'Source_Value': 'MISSING',
                'Target_Value': order_id
            })

    # -------------------------------------------------------------
    # 4. Generate Exception Artifact
    # -------------------------------------------------------------
    fieldnames = ['Order_ID', 'Issue', 'Field', 'Source_Value', 'Target_Value']
    with open(REPORT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(exceptions)

    # Console Summary Metrics
    print("=" * 45)
    print("        RECONCILIATION SUMMARY REPORT        ")
    print("=" * 45)
    print(f"Total Source Unique Records : {len(source_records)}")
    print(f"Total Target Unique Records : {len(target_records)}")
    print(f"Total Exceptions Identified : {len(exceptions)}")
    print("=" * 45)


if __name__ == "__main__":
    run_reconciliation()
