import csv

def load_data(file_path):
    """Reads a CSV file into a dictionary keyed by Order_ID."""
    data = {}
    duplicates = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['Order_ID']
            if order_id in data:
                duplicates.append(row)
            else:
                data[order_id] = row
    return data, duplicates

def run_reconciliation():
    source, source_dups = load_data('data/source_orders.csv')
    target, target_dups = load_data('data/target_orders.csv')

    exceptions = []

    # 1. Check for target duplicates
    for dup in target_dups:
        exceptions.append({
            'Order_ID': dup['Order_ID'],
            'Issue': 'Duplicate in target',
            'Field': 'All',
            'Source_Value': 'N/A',
            'Target_Value': 'Duplicate Record'
        })

    # 2. Check source against target
    for order_id, source_row in source.items():
        if order_id not in target:
            exceptions.append({
                'Order_ID': order_id,
                'Issue': 'Missing in target',
                'Field': 'Order_ID',
                'Source_Value': order_id,
                'Target_Value': 'Missing'
            })
        else:
            target_row = target[order_id]
            # Check for value mismatches across fields
            for field in ['Customer_ID', 'Order_Date', 'Order_Amount', 'Order_Status', 'Currency']:
                if source_row[field] != target_row[field]:
                    exceptions.append({
                        'Order_ID': order_id,
                        'Issue': f'{field} mismatch',
                        'Field': field,
                        'Source_Value': source_row[field],
                        'Target_Value': target_row[field]
                    })

    # 3. Check for records missing in source (Unexpected/New in target)
    for order_id in target:
        if order_id not in source:
            exceptions.append({
                'Order_ID': order_id,
                'Issue': 'Missing in source / Unexpected',
                'Field': 'Order_ID',
                'Source_Value': 'Missing',
                'Target_Value': order_id
            })

    # 4. Write exception report to results/exceptions.csv
    fieldnames = ['Order_ID', 'Issue', 'Field', 'Source_Value', 'Target_Value']
    with open('results/exceptions.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(exceptions)

    print(f"Reconciliation completed. Found {len(exceptions)} exceptions.")

if __name__ == "__main__":
    run_reconciliation()
