import sqlite3
import os

# OrcheFlowAI — Local Database Seeder
# Ensures the demo user exists in the local SQLite fallback for offline demo stability.

# Path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'sample_data', 'local_demo.db')

print(f"!! [SEEDER] Target DB: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist (safety)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            timezone TEXT,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert Demo User
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, email, timezone, preferences) 
        VALUES ('01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f', 'demo@example.com', 'UTC', '{}')
    """)
    
    conn.commit()
    print("✅ [SEEDER] Demo user verified/inserted.")
    conn.close()
except Exception as e:
    print(f"❌ [SEEDER] Error: {e}")
