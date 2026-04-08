import sqlite3
c = sqlite3.connect('local_demo.db')
c.execute("INSERT INTO users (id, email, timezone, preferences) VALUES ('01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f', 'demo@example.com', 'UTC', '{}')")
c.commit()
print("Seeded user")
