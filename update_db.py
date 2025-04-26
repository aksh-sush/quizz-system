# just for verification
#no need of this file


import sqlite3

# Connect to your existing database
conn = sqlite3.connect('database.db')
c = conn.cursor()


# Try to add the 'correct' column to the questions table
try:
    c.execute("ALTER TABLE questions ADD COLUMN correct TEXT")
    print("✅ 'correct' column added to the questions table.")
except sqlite3.OperationalError as e:
    print("⚠️ Error:", e)


conn.commit()
conn.close()
