import sqlite3

conn = sqlite3.connect('quiz_system.db')  # Make sure path is correct
cursor = conn.cursor()

# List all tables
print("📋 Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print("-", table[0])

# Check structure of quizzes table
print("\n📌 Structure of 'quizzes' table:")
cursor.execute("PRAGMA table_info(quizzes);")
columns = cursor.fetchall()
for col in columns:
    print(f"- {col[1]} ({col[2]})")  # column name and type

conn.close()
