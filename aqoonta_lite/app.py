 from flask import Flask, render_template, request
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

db_connection = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)

# Simple in-memory caches
_cached_lessons_manifest = None
_cached_lesson_contents = {}
_cached_quiz_questions = {}

def get_lessons_manifest():
    global _cached_lessons_manifest
    if _cached_lessons_manifest is None:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, title FROM lessons ORDER BY id;")
            _cached_lessons_manifest = cursor.fetchall()
    return _cached_lessons_manifest

def get_lesson_content_by_id(lesson_id):
    if lesson_id not in _cached_lesson_contents:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, title, topic, content FROM lessons WHERE id = %s;", (lesson_id,))
            lesson_content = cursor.fetchone()
            _cached_lesson_contents[lesson_id] = lesson_content
    return _cached_lesson_contents[lesson_id]

def get_quiz_questions_by_lesson_id(lesson_id):
    if lesson_id not in _cached_quiz_questions:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT question, option_a, option_b, option_c, option_d, correct_option 
                FROM quizzes WHERE lesson_id = %s ORDER BY id;
            """, (lesson_id,))
            questions = cursor.fetchall()
            _cached_quiz_questions[lesson_id] = questions
    return _cached_quiz_questions[lesson_id]

def grade_quiz_answers(lesson_id, submitted_answers):
    questions = get_quiz_questions_by_lesson_id(lesson_id)
    total_questions = len(questions)
    score = 0
    for index, question in enumerate(questions):
        correct_answer_index = ord(question['correct_option'].upper()) - ord('A')
        selected_answer = submitted_answers.get(f'q{index}')
        if selected_answer and selected_answer.isdigit() and int(selected_answer) == correct_answer_index:
            score += 1
    return score, total_questions

@app.route('/')
def main_dashboard():
    lessons = get_lessons_manifest()
    return render_template('main_page.html', lessons=lessons)

@app.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    lesson = get_lesson_content_by_id(lesson_id)
    if not lesson:
        return "<h1>Lesson not found</h1>", 404
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM quizzes WHERE lesson_id = %s;", (lesson_id,))
        quiz_available = cursor.fetchone()[0] > 0
    return render_template('lesson_page.html', lesson=lesson, quiz_exists=quiz_available)

@app.route('/quiz/<int:lesson_id>', methods=['GET', 'POST'])
def quiz_page(lesson_id):
    questions = get_quiz_questions_by_lesson_id(lesson_id)
    if not questions:
        return "<h1>Quiz not found</h1>", 404
    result_message = None
    if request.method == 'POST':
        score, total = grade_quiz_answers(lesson_id, request.form)
        result_message = f"You scored {score} out of {total}."
    return render_template('quiz_page.html', questions=questions, lesson_id=lesson_id, result=result_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
