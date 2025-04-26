import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
     # ✅ Create quizzes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            instructor_id INTEGER NOT NULL,
            FOREIGN KEY (instructor_id) REFERENCES users(id)
        )
    ''')
 
    c.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct TEXT,
        image_path TEXT,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    )
''')

    conn.commit()
    conn.close()
    # Create submissions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    quiz_id INTEGER,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
)
''')

# Create student_answers table to store answers for each student and each question
    c.execute('''
    CREATE TABLE IF NOT EXISTS student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER,
    question_id INTEGER,
    answer TEXT,
    FOREIGN KEY (submission_id) REFERENCES submissions(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
)
''')


def register_user(email, password, role):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_user(email, password):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'email': user[1],
            'password': user[2],
            'role': user[3]
        }
    return None
def get_quizzes_by_instructor(instructor_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, title, code FROM quizzes WHERE instructor_id = ?", (instructor_id,))
    quizzes = c.fetchall()
    conn.close()
    return quizzes
import sqlite3

def get_all_quizzes():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT title, code FROM quizzes")
    quizzes = c.fetchall()
    conn.close()
    return quizzes


def create_quiz(title, code, instructor_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO quizzes (title, code, instructor_id) VALUES (?, ?, ?)", (title, code, instructor_id))
    quiz_id = cur.lastrowid  # <-- This gets the new quiz ID
    conn.commit()
    conn.close()
    return quiz_id  # <-- Return it!



def add_question(quiz_id, question, a, b, c, d, correct, image_path):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()  # Changed from 'c' to 'cursor'
    cursor.execute('''
        INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (quiz_id, question, a, b, c, d, correct, image_path))
    conn.commit()
    conn.close()

def get_questions_by_quiz(quiz_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = c.fetchall()
    conn.close()
    return questions

def delete_question_by_id(question_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


def get_question_by_id(question_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions WHERE id=?", (question_id,))
    question = cur.fetchone()
    conn.close()
    return question


def update_question_by_id(question_id, question, a, b, c, d, correct, image_path=None):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if image_path:
        cur.execute('''
            UPDATE questions
            SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct = ?, image_path = ?
            WHERE id = ?
        ''', (question, a, b, c, d, correct, image_path, question_id))
    else:
        cur.execute('''
            UPDATE questions
            SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct = ?
            WHERE id = ?
        ''', (question, a, b, c, d, correct, question_id))
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        quiz_id INTEGER,
        question_id INTEGER,
        answer TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
 