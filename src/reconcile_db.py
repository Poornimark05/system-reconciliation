import sqlite3
import csv

DB_PATH = 'data/reconciliation.db'
REPORT_FILE = 'results/exceptions.csv'

def run_db_reconciliation():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    exceptions = []

    # 1. SQL Rule: Identify Duplicate Keys in Target
    dup_query = """
    SELECT Order_ID, COUNT(*) 
    FROM target_orders 
    GROUP BY Order_ID 
    HAVING COUNT(*) > 1;
    """
    cursor.execute(dup_query)
    for row in cursor.fetchall():
        exceptions.append({
            'Order_ID': row[0],
            'Issue': 'Duplicate in target',
            'Field': 'Order_ID',
            'Source_Value': 'N/A',
            'Target_Value': f'Duplicate Count: {row[1]}'
        })

    # 2. SQL Rule: Compare Source against Target (Missing in Target + Field Mismatches)
    reconcile_query = """
    SELECT 
        s.Order_ID AS Source_Order_ID,
        t.Order_ID AS Target_Order_ID,
        s.Customer_ID, t.Customer_ID,
        s.Order_Date, t.Order_Date,
        s.Order_Amount, t.Order_Amount,
        s.Order_Status, t.Order_Status,
        s.Currency, t.Currency
    FROM source_orders s
    LEFT JOIN target_orders t ON s.Order_ID = t.Order_ID;
    """
    cursor.execute(reconcile_query)
    source_matches = cursor.fetchall()

    for row in source_matches:
        src_id = row[0]
        tgt_id = row[1]

        # Missing in Target check
        if tgt_id is None:
            exceptions.append({
                'Order_ID': src_id,
                'Issue': 'Missing in target',
                'Field': 'Order_ID',
                'Source_Value': src_id,
                'Target_Value': 'Missing'
            })
        else:
            # Field Mismatch checks
            fields = ['Customer_ID', 'Order_Date', 'Order_Amount', 'Order_Status', 'Currency']
            for idx, field in enumerate(fields):
                src_val = str(row[2 + idx * 2])
                tgt_val = str(row[3 + idx * 2])
                if src_val != tgt_val:
                    exceptions.append({
                        'Order_ID': src_id,
                        'Issue': f'{field} mismatch',
                        'Field': field,
                        'Source_Value': src_val,
                        'Target_Value': tgt_val
                    })

    # 3. SQL Rule: Identify Unexpected Records in Target (Missing in Source)
    unexpected_query = """
    SELECT t.Order_ID 
    FROM target_orders t
    LEFT JOIN source_orders s ON t.Order_ID = s.Order_ID
    WHERE s.Order_ID IS NULL;
    """
    cursor.execute(unexpected_query)
    for row in cursor.fetchall():
        exceptions.append({
            'Order_ID': row[0],
            'Issue': 'Missing in source / Unexpected',
            'Field': 'Order_ID',
            'Source_Value': 'Missing',
            'Target_Value': row[0]
        })

    conn.close()

    # Write output report
    fieldnames = ['Order_ID', 'Issue', 'Field', 'Source_Value', 'Target_Value']
    with open(REPORT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(exceptions)

    print(f"Database Reconciliation completed. Found {len(exceptions)} exceptions.")

if __name__ == "__main__":
    run_db_reconciliation()