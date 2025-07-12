# app.py
from flask import Flask, Response, request, url_for
import json
import os

app = Flask(__name__)

# --- Helper functions to load data ---
def load_lessons_manifest():
    """
    Loads the manifest of available lessons from the 'data/lessons' directory.
    Each lesson file (e.g., 'finance.json') becomes an entry in the manifest.
    """
    lessons = []
    lessons_dir = 'data/lessons'
    if not os.path.exists(lessons_dir):
        print(f"Warning: Lessons directory '{lessons_dir}' not found.")
        return []

    lesson_files = [f for f in os.listdir(lessons_dir) if f.endswith('.json')]
    for f in lesson_files:
        topic_id = os.path.splitext(f)[0]
        # Try to load the actual title from the JSON file if available
        try:
            with open(os.path.join(lessons_dir, f), 'r', encoding='utf-8') as lf:
                lesson_data = json.load(lf)
                title = lesson_data.get('title', topic_id.replace('_', ' ').title())
        except (FileNotFoundError, json.JSONDecodeError):
            title = topic_id.replace('_', ' ').title() # Fallback title
        lessons.append({'id': topic_id, 'name': title})
    return lessons


def load_lesson_content(topic):
    """
    Loads the content of a specific lesson based on its topic ID.
    """
    file_path = os.path.join('data/lessons', f'{topic}.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Lesson file not found for topic '{topic}' at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from lesson file for topic '{topic}' at {file_path}")
        return None

def load_quiz_questions(topic):
    """
    Loads the quiz questions for a specific topic from the 'data/quizzes' directory.
    """
    file_path = os.path.join('data/quizzes', f'{topic}_quiz.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Quiz file not found for topic '{topic}' at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from quiz file for topic '{topic}' at {file_path}")
        return None

def check_quiz_answers(topic, submitted_answers):
    """
    Checks the submitted answers against the correct answers for a given quiz topic.
    Returns the score and a message.
    """
    questions = load_quiz_questions(topic)
    if not questions:
        return 0, "Quiz not found or questions could not be loaded."

    score = 0
    for i, question in enumerate(questions):
        submitted_option = submitted_answers.get(f'q{i}')
        if submitted_option is not None:
            try:
                if int(submitted_option) == question['answer']:
                    score += 1
            except ValueError:
                pass # Ignore if submitted option is not a valid integer

    return score, f"You scored {score} out of {len(questions)}."

# --- HTML Generation Functions (for direct Response) ---
def _get_main_page_html(lessons):
    """Generates the HTML for the main dashboard page."""
    lessons_html = ""
    if lessons:
        for lesson in lessons:
            lessons_html += f"<li><a href=\"{url_for('lesson_detail', topic=lesson['id'])}\">{lesson['name']}</a></li>"
    else:
        lessons_html = "<p>No lessons available yet.</p>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Learning Dashboard</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin-bottom: 10px; }}
            a {{ text-decoration: none; color: #007bff; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>Welcome to the Learning App!</h1>

        <h2>Lessons</h2>
        <ul>
            {lessons_html}
        </ul>

        <h2>Quizzes</h2>
        <ul>
            <li><a href="{url_for('quiz_page', topic='business')}">Business Quiz</a></li>
            </ul>
    </body>
    </html>
    """

def _get_lesson_page_html(topic, content, quiz_exists):
    """Generates the HTML for a specific lesson's detail page."""
    sections_html = ""
    if content and content.get('sections'):
        for section in content['sections']:
            sections_html += f"<h2>{section.get('heading', 'No Heading')}</h2><p>{section.get('content', 'No Content')}</p>"
    else:
        sections_html = "<p>No content available for this lesson.</p>"

    quiz_link_html = ""
    if quiz_exists:
        quiz_link_html = f"<a href=\"{url_for('quiz_page', topic=topic)}\">Take Quiz</a>"
    else:
        quiz_link_html = "<span>(No quiz available for this topic)</span>"

    lesson_title = content.get('title', 'Lesson') if content else 'Lesson'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{lesson_title}</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            .section-content {{ margin-bottom: 15px; }}
            .navigation-links a {{ margin-right: 15px; }}
        </style>
    </head>
    <body>
        <h1>{lesson_title}</h1>

        {sections_html}

        <div class="navigation-links">
            <a href="{url_for('main_dashboard')}">Back to Dashboard</a>
            {quiz_link_html}
        </div>
    </body>
    </html>
    """

def _get_quiz_page_html(topic, questions, result_message, form_data):
    """Generates the HTML for the quiz page, handling all logic in Python."""
    questions_html = ""
    if questions:
        for i, question in enumerate(questions): # Using Python's enumerate here
            options_html = ""
            for j, option in enumerate(question.get('options', [])): # Using Python's enumerate here
                # Check if the current option was selected in the submitted form data
                # form_data values are strings, so convert j to string for comparison
                checked = 'checked' if form_data.get(f'q{i}') == str(j) else ''
                options_html += f"""
                    <label>
                        <input type='radio' id='q{i}o{j}' name='q{i}' value='{j}' {checked}>
                        {option}
                    </label><br>
                """
            questions_html += f"""
                <div class="question">
                    <p><strong>{i + 1}. {question.get('question', 'No Question')}</strong></p>
                    <div class="options">
                        {options_html}
                    </div>
                </div>
            """
        submit_button = "<input type=\"submit\" value=\"Submit Quiz\">"
    else:
        questions_html = "<p class=\"error-message\">No questions available for this quiz.</p>"
        submit_button = ""

    result_message_html = f"<p class=\"result-message\">{result_message}</p>" if result_message else ""

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{topic.replace('_', ' ').title()} Quiz</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            .question {{ margin-bottom: 20px; }}
            .options label {{ display: block; margin-bottom: 5px; }}
            .result-message {{ font-weight: bold; margin-top: 20px; color: green; }}
            .error-message {{ font-weight: bold; margin-top: 20px; color: red; }}
            .navigation-links a {{ margin-right: 15px; }}
        </style>
    </head>
    <body>
        <h1>{topic.replace('_', ' ').title()} Quiz</h1>

        {result_message_html}

        <form method="POST">
            {questions_html}
            {submit_button}
        </form>

        <div class="navigation-links" style="margin-top: 20px;">
            <a href="{url_for('lesson_detail', topic=topic)}">Back to Lesson</a>
            <a href="{url_for('main_dashboard')}">Back to Dashboard</a>
        </div>
    </body>
    </html>
    """

# --- Routes ---
@app.route('/')
def main_dashboard():
    """
    Renders the main dashboard page, listing all available lessons.
    """
    lessons = load_lessons_manifest()
    return Response(_get_main_page_html(lessons), mimetype='text/html')

@app.route('/lesson/<string:topic>')
def lesson_detail(topic):
    """
    Renders the detail page for a specific lesson.
    """
    content = load_lesson_content(topic)
    if content is None:
        return Response("<h1>Lesson not found!</h1>", mimetype='text/html', status=404)
    # Check if a quiz exists for this topic to enable the quiz link
    quiz_exists = os.path.exists(os.path.join('data/quizzes', f'{topic}_quiz.json'))
    return Response(_get_lesson_page_html(topic, content, quiz_exists), mimetype='text/html')

@app.route('/quiz/<string:topic>', methods=['GET', 'POST'])
def quiz_page(topic):
    """
    Handles displaying the quiz and processing submitted answers.
    """
    questions = load_quiz_questions(topic)
    if not questions:
        return Response("<h1>Quiz not found or empty! Please ensure the quiz JSON file is correctly populated.</h1>", mimetype='text/html', status=404)

    result_message = None
    form_data = {} # To preserve user's answers on POST

    if request.method == 'POST':
        form_data = request.form
        score, message = check_quiz_answers(topic, form_data)
        result_message = message

    # For GET requests or after POST, render the quiz page
    return Response(_get_quiz_page_html(topic, questions, result_message, form_data), mimetype='text/html')

if __name__ == '__main__':
    # Ensure necessary directories exist for data storage
    os.makedirs('data/lessons', exist_ok=True)
    os.makedirs('data/quizzes', exist_ok=True)
    # No 'templates' directory needed when generating HTML directly

    app.run(debug=True)