import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM taken_quizzes")
rows = cur.fetchall()

print("Taken Quizzes:")
for row in rows:
    print(f"User ID: {row['user_id']}, Quiz ID: {row['quiz_id']}")

conn.close()
