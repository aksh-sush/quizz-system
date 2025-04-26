import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# ❗ Delete all users (be careful!)
# c.execute("DELETE FROM users")

# ✅ Or delete a specific user by email
email_to_delete = "arun@gmail.com"
c.execute("DELETE FROM users WHERE email = ?", (email_to_delete,))

conn.commit()
conn.close()

print("User(s) deleted successfully.")
