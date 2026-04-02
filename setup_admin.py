import sqlite3

# Connect directly to the SQLite database
# The database file is likely located in the backend/ directory or root. Let's find it.
import os

db_path = None
if os.path.exists("backend/lottery.db"):
    db_path = "backend/lottery.db"
elif os.path.exists("lottery.db"):
    db_path = "lottery.db"
else:
    print("Error: Could not find lottery.db")
    exit(1)

print(f"Using database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if james@moderncyph3r.com exists
cursor.execute("SELECT id FROM users WHERE email = 'james@moderncyph3r.com'")
result = cursor.fetchone()

if result:
    print("User exists. Updating to Admin & Pro Tier...")
    cursor.execute("UPDATE users SET is_admin = 1, tier = 'pro' WHERE email = 'james@moderncyph3r.com'")
else:
    print("User does not exist. Creating Admin & Pro Tier user...")
    cursor.execute("INSERT INTO users (email, tier, is_admin, is_active) VALUES ('james@moderncyph3r.com', 'pro', 1, 1)")

conn.commit()
print("Success.")
conn.close()
