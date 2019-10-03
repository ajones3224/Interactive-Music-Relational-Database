__author__ = 'Rachel Williams'

from flask import Flask, render_template, request, session
import queries

app = Flask(__name__)

# secret key for session
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return render_template('start_page.html')

@app.route('/q_page.html', methods = ['GET', 'POST'])
def set_q_data():
    all_questions = queries.createQuestions() 
    session['questions'] = len(all_questions)
    return render_template('q_page.html', result=all_questions)

@app.route('/end_page.html', methods = ['GET', 'POST'])
def nothing():
    if session.get('questions', None):
        quiz_length = session.get('questions', None)
    else:
        quiz_length = 0
    session.clear()
    return render_template('end_page.html', quiz_length=quiz_length)

if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 5000)