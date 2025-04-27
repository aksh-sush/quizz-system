from flask import Flask, render_template, request, redirect, url_for, session
from models.models import init_db, register_user, validate_user
import os
import sqlite3
from models.models import get_questions_by_quiz
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize database

init_db()

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        success = register_user(email, password, role)
        if success:
            return redirect('/login')
        else:
            return "User already exists"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            if user['role'] == 'instructor':
                return redirect('/instructor_dashboard')
            elif user['role'] == 'student':
                return redirect('/student_dashboard')
            elif user['role'] == 'admin':
                return redirect('/admin/dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect('/login')  # Redirect to login page

@app.route('/instructor_dashboard')
def instructor_dashboard():
    # Check if the instructor is logged in (this ensures `session` is valid)
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')  # or some other page if not logged in

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get the instructor_id from the session
    instructor_id = session.get('user_id')  # Get the user ID from the session

    if not instructor_id:  # Handle the case if instructor_id is not found
        return redirect('/login')  # or any other page to handle the error

    # Get all quizzes by the instructor
    cur.execute("SELECT * FROM quizzes WHERE instructor_id = ?", (instructor_id,))
    quizzes = cur.fetchall()

    # Count how many students have taken each quiz
    quiz_counts = {}
    for quiz in quizzes:
        cur.execute("SELECT COUNT(*) FROM taken_quizzes WHERE quiz_id = ?", (quiz['id'],))
        count = cur.fetchone()[0]
        quiz_counts[quiz['id']] = count

    conn.close()

    return render_template('instructor_dashboard.html', quizzes=quizzes, quiz_counts=quiz_counts)


@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'user_id' not in session or session['role'] != 'instructor':
        return redirect('/login')

    from models.models import create_quiz

    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        instructor_id = session['user_id']
        quiz_id = create_quiz(title, code, instructor_id)  # <-- get the new quiz ID
        return redirect(f'/add_question/{quiz_id}')  # <-- redirect to add question

    return render_template('create_quiz.html')


@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz_route():
    if 'user_id' not in session or session['role'] != 'instructor':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        instructor_id = session['user_id']

        try:
            create_quiz(title, code, instructor_id)
            return redirect('/instructor_dashboard')
        except ValueError as e:
            return render_template('create_quiz.html', error=str(e))  # ✅ Pass error to the template

    return render_template('create_quiz.html')



from flask import request, redirect, url_for, render_template, session, flash
import os
from werkzeug.utils import secure_filename
from models.models import add_question

# Route to add questions
@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question_route(quiz_id):
    if request.method == 'POST':
        question = request.form['question']
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        d = request.form['d']
        correct = request.form['correct']
        image = request.files.get('image')

        image_path = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_folder = os.path.join(app.root_path, 'static', 'images')
            os.makedirs(image_folder, exist_ok=True)  # ensures folder exists
            full_path = os.path.join(image_folder, filename)
            image.save(full_path)
            image_path = 'images/' + filename  # This will be stored in DB

        add_question(quiz_id, question, a, b, c, d, correct, image_path)
        return redirect(f'/view_questions/{quiz_id}')

    return render_template('add_question.html', quiz_id=quiz_id)


# Route to view questions
@app.route('/view_questions/<int:quiz_id>')
def view_questions(quiz_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = c.fetchall()

    c.execute("SELECT title FROM quizzes WHERE id=?", (quiz_id,))
    quiz_title = c.fetchone()[0]
    conn.close()

    return render_template('view_questions.html', questions=questions, quiz_title=quiz_title)

from models.models import delete_question_by_id

@app.route('/delete_question/<int:question_id>')
def delete_question(question_id):
    delete_question_by_id(question_id)
    return redirect(request.referrer or '/')


from flask import render_template, request, redirect, url_for
from models.models import get_question_by_id, update_question_by_id
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'POST':
        question = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct = request.form['correct']

        image_file = request.files.get('image')
        image_path = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

        update_question_by_id(question_id, question, option_a, option_b, option_c, option_d, correct, image_path)
        return redirect(url_for('instructor_dashboard'))
    else:
        question_data = get_question_by_id(question_id)
        return render_template('edit_question.html', question=question_data)
from models.models import get_all_quizzes  # Import the missing function
@app.route('/student_dashboard/')
def student_dashboard():
    # Connect to the database
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Ensures rows are returned as dictionaries
    cur = conn.cursor()

    # Execute the query to get quizzes
    cur.execute("SELECT * FROM quizzes")
    quizzes = cur.fetchall()  # Now quizzes should be a list of Row objects (not tuples)
    user_id = 1  # or session user
    # Get quiz IDs that have been answered by the student (check if any response exists for any quiz)
    cur.execute("SELECT DISTINCT quiz_id FROM responses")
    answered_quiz_ids = {row[0] for row in cur.fetchall()}
    taken_quiz_ids = [row[0] for row in cur.fetchall()]

    conn.close()

    # Pass quizzes and the answered_quiz_ids to the template
    return render_template("student_dashboard.html", quizzes=quizzes, answered_quiz_ids=answered_quiz_ids, taken_quiz_ids=taken_quiz_ids)

@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Fetch quiz title and questions
    cur.execute("SELECT title FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cur.fetchone()
    if not quiz:
        return "Quiz not found", 404
    
    cur.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = cur.fetchall()

    user_id = 1  # Replace this with session value later

    if request.method == 'POST':
        # Collect answers
        answers = {}
        for q in questions:
            qid = q['id']
            user_answer = request.form.get(f'q{qid}')
            if user_answer:
                answers[qid] = user_answer

        # Insert responses
        for qid, user_answer in answers.items():
            cur.execute("INSERT INTO responses (quiz_id, question_id, answer) VALUES (?, ?, ?)",
                        (quiz_id, qid, user_answer))

        # Mark quiz as taken
        cur.execute("INSERT OR IGNORE INTO taken_quizzes (user_id, quiz_id) VALUES (?, ?)", (user_id, quiz_id))

        conn.commit()
        conn.close()
        return redirect(url_for('student_dashboard'))  # Redirect after submission

    # Fetch taken quizzes for this user
    cur.execute("SELECT quiz_id FROM taken_quizzes WHERE user_id = ?", (user_id,))
    taken = cur.fetchall()
    taken_quiz_ids = [row['quiz_id'] for row in taken]

    conn.close()
    return render_template(
        'take_quiz.html',
        quiz_id=quiz_id,
        quiz_title=quiz['title'],
        questions=questions,
        taken_quiz_ids=taken_quiz_ids
    )

import sqlite3

# Create the table if it doesn't exist
def create_taken_quizzes_table():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS taken_quizzes (
            user_id INTEGER,
            quiz_id INTEGER,
            PRIMARY KEY (user_id, quiz_id)
        )
    ''')

    conn.commit()
    conn.close()
    
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect('/login')
    
    student_id = session['user_id']
    quiz_id = request.form['quiz_id']
    answers = request.form.getlist('answers')  # Assuming answers are sent as a list of question IDs with their answers

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Step 1: Insert into the submissions table
    cur.execute('''
        INSERT INTO submissions (student_id, quiz_id)
        VALUES (?, ?)
    ''', (student_id, quiz_id))

    # Get the last inserted submission_id
    submission_id = cur.lastrowid

    # Step 2: Insert each answer into the student_answers table
    for question_id, answer in answers:
        cur.execute('''
            INSERT INTO student_answers (submission_id, question_id, answer)
            VALUES (?, ?, ?)
        ''', (submission_id, question_id, answer))

    conn.commit()
    conn.close()

    return redirect('/quiz_submission_success')@app.route('/view_results/<int:quiz_id>')


def view_results(quiz_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This ensures rows are returned as dictionaries
    cur = conn.cursor()

    # Query to get quiz results, including student username, quiz title, and the correct count
    cur.execute("""
        SELECT 
            sa.quiz_id, 
            s.username AS student_username, 
            sa.correct_count, 
            q.title AS quiz_title 
        FROM student_answers sa
        JOIN students s ON sa.student_username = s.username
        JOIN quizzes q ON sa.quiz_id = q.id
        WHERE sa.quiz_id = ?
    """, (quiz_id,))

    student_answers = cur.fetchall()
    conn.close()

    return render_template('view_results.html', student_answers=student_answers)

if __name__ == '__main__':
    app.run(debug=True)
