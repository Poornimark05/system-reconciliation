import sqlite3
import csv
import os

DB_PATH = 'data/reconciliation.db'
SOURCE_CSV = 'data/source_orders.csv'
TARGET_CSV = 'data/target_orders.csv'

def create_and_populate_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    schema = """
    CREATE TABLE {table_name} (
        Order_ID TEXT,
        Customer_ID TEXT,
        Order_Date TEXT,
        Order_Amount REAL,
        Order_Status TEXT,
        Currency TEXT
    );
    """

    cursor.execute(schema.format(table_name='source_orders'))
    cursor.execute(schema.format(table_name='target_orders'))

    def load_csv_to_table(csv_path, table_name):
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [(r['Order_ID'], r['Customer_ID'], r['Order_Date'], 
                     float(r['Order_Amount']), r['Order_Status'], r['Currency']) for r in reader]
            
            cursor.executemany(
                f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?)", rows
            )

    load_csv_to_table(SOURCE_CSV, 'source_orders')
    load_csv_to_table(TARGET_CSV, 'target_orders')

    conn.commit()
    conn.close()
    print("SQLite database built successfully at 'data/reconciliation.db'.")

if __name__ == "__main__":
    create_and_populate_db()