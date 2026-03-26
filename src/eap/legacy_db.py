import sqlite3
import os

def seed_legacy_mainframe():
    print("💾 Booting Legacy Mainframe Seeder...")
    
    # 1. Connect to the SQL database (creates it if it doesn't exist)
    conn = sqlite3.connect("mainframe.db")
    cursor = conn.cursor()
    
    # 2. Create the Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            client_id TEXT PRIMARY KEY, 
            name TEXT, 
            balance REAL, 
            tier TEXT
        )
    ''')
    
    # Clear existing data so we can run this multiple times safely (Idempotency)
    cursor.execute("DELETE FROM accounts")
    
    # 3. Insert Mock Banking Clients
    clients =[
        ("C-12345", "Alice Smith", 8500.00, "Tier 1"),   # Not enough money for a $15k trade!
        ("C-98765", "Bob Jones", 150000.00, "Tier 1"), # Wealthy client
    ]
    
    cursor.executemany("INSERT INTO accounts VALUES (?, ?, ?, ?)", clients)
    conn.commit()
    conn.close()
    
    print("✅ Legacy SQL Database 'mainframe.db' seeded successfully.")

if __name__ == "__main__":
    seed_legacy_mainframe()