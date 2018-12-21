import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, escape

app = Flask(__name__)
app.secret_key = '123456'

def openDbCon():
    DATABASE = 'hw13.db'
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    con = openDbCon()
    cursor = con.cursor()
    with app.open_resource('schema.sql', mode = 'r') as schema_file:
        cursor.executescript(schema_file.read())
    con.commit()
    cursor.close()


# Initialize database from schema.sql
init_db()


@app.route('/')
def index(): 
    current_user_id = 0
    if 'user_id' in session:
        current_user_id = session['user_id']

    if 'error' in session:
        error = session['error']
        session.pop('error')

    if 'msg' in session:
        msg = session['msg']
        session.pop('msg')

    if current_user_id == 0:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('dashboard'))


# Dashboard controller
@app.route('/dashboard')
def dashboard():
    current_user_id = 0
    error = None
    msg = None
    if 'user_id' in session:
        current_user_id = session['user_id']

    if 'error' in session:
        error = session['error']
        session.pop('error')

    if 'msg' in session:
        msg = session['msg']
        session.pop('msg')

    if current_user_id == 0:
        return redirect(url_for('login'))
    else:
        students = list()
        quizzes = list()

        cursor = openDbCon().cursor()

        # Fetch students
        cursor.execute('SELECT id, firstname, lastname FROM students')
        for student in cursor:
            students.append({
                "id" : student[0],
                "firstname" : student[1],
                "lastname" : student[2],
            })

        # Fetch quizzes
        cursor.execute('SELECT id, subject, no_of_questions, date FROM quizzes')
        for quiz in cursor:
            quizzes.append({
                "id" : quiz[0],
                "subject" : quiz[1],
                "no_of_questions" : quiz[2],
                "date" : quiz[3],
            })

        cursor.close()

        return render_template('dashboard.html', error = error, msg = msg, students = students, quizzes = quizzes)


# Login Controller
@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = None
    username = ''
    password = ''

    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if 'username' in request.form:
            username = request.form['username']
        
        if 'password' in request.form:
            password = request.form['password']


        if not username or not password:
            error = 'Username or Password is empty'

        # Dummy Teacher authentication goes here.
        if username == 'admin' and password == 'password':
            session['user_id'] = 1 # Assigning a dummy static user id to simulate authentication.
        else:
            error = 'Invalid Username or Password'
    else:
        return render_template('login.html')

    if error:
        return render_template('login.html', error = error)
    else:
        session['msg'] = "Login successful. Welcome Teacher."
        return redirect(url_for('dashboard'))
    
    

# Logout Controller
@app.route('/logout', methods = ['GET'])
def logout():
    for key in session.keys():
        session.pop(key)
    return redirect(url_for('index'))



# Add Student Controller
@app.route('/student/add', methods = ['POST', 'GET'])
def add_student():
    current_user_id = 0
    error = None
    firstname = None
    lastname = None

    if 'user_id' in session:
        current_user_id = session['user_id']
    else:
        return redirect(url_for('login')) 

    if current_user_id != 0 and request.method == 'POST':
        if 'firstname' in request.form:
            firstname = request.form['firstname']
        
        if 'lastname' in request.form:
            lastname = request.form['lastname']


        if not firstname:
            error = 'Firstname is empty'
        elif not lastname:
            error = 'Lastname is empty'

        if not error:
            # Insert student in DB
            con = openDbCon()
            cursor = con.cursor()

            cursor.execute(
            "INSERT INTO students(firstname, lastname) values (?, ?)", 
            (firstname, lastname,))

            con.commit()
            cursor.close()
    else:
        return render_template('form_add_student.html')

    if error:
        return render_template('form_add_student.html', error = error)
    else:
        session['msg'] = "Student Added Successfully."
        return redirect(url_for('dashboard'))


# Delete student Controller
@app.route('/student/delete', methods = ['POST', 'GET'])
def delete_student():
    current_user_id = 0
    error = None

    if 'user_id' in session:
        current_user_id = session['user_id']

    student_id = None

    if current_user_id != 0 and request.method == 'POST':
        if 'id' in request.form:
            student_id = request.form['id']
        

        if not student_id:
            error = 'Error! Unable to delete student.'
        else:
            # Delete students in DB
            con = openDbCon()
            cursor = con.cursor()

            # Check if student already exists
            cursor.execute('SELECT * FROM students WHERE (id=?)', (student_id,))
            check = cursor.fetchone()
            if check is None:
                error = "Unable to find student."
            else:
                cursor.execute(
                "DELETE FROM students WHERE (id=?)", 
                (student_id, ))
                
            con.commit()
            cursor.close()      
    else:
        return redirect(url_for('dashboard'))

    if error:
        session['error'] = error
    else:
        session['msg'] = "Student delete sucessfully"      

    return redirect(url_for('dashboard'))


# Add Quiz Controller
@app.route('/quiz/add', methods = ['POST', 'GET'])
def add_quiz():
    current_user_id = 0
    error = None
    subject = None
    no_of_questions = None
    date = None

    if 'user_id' in session:
        current_user_id = session['user_id']
    else:
        return redirect(url_for('login')) 

    if current_user_id != 0 and request.method == 'POST':
        if 'subject' in request.form:
            subject = request.form['subject']
        
        if 'no_of_questions' in request.form:
            no_of_questions = request.form['no_of_questions']

        if 'date' in request.form:
            date = request.form['date']


        if not subject:
            error = 'Subject is empty'
        elif not no_of_questions:
            error = 'No. of questions is empty'
        elif not date:
            error = 'Date is empty'

        if not error:
            # Insert quiz in DB
            con = openDbCon()
            cursor = con.cursor()

            cursor.execute(
            "INSERT INTO quizzes(subject, no_of_questions, date) values (?, ?, ?)", 
            (subject, no_of_questions, date, ))

            con.commit()
            cursor.close()
    else:
        return render_template('form_add_quiz.html')

    if error:
        return render_template('form_add_quiz.html', error = error)
    else:
        session['msg'] = "Student Added Successfully."
        return redirect(url_for('dashboard'))

# Delete quiz Controller
@app.route('/quiz/delete', methods = ['POST', 'GET'])
def delete_quiz():
    current_user_id = 0
    error = None

    if 'user_id' in session:
        current_user_id = session['user_id']

    quiz_id = None

    if current_user_id != 0 and request.method == 'POST':
        if 'id' in request.form:
            quiz_id = request.form['id']
        

        if not quiz_id:
            error = 'Error! Unable to delete quiz.'
        else:
            # Delete quiz in DB
            con = openDbCon()
            cursor = con.cursor()

            # Check if quiz already exists
            cursor.execute('SELECT * FROM quizzes WHERE (id=?)', (quiz_id,))
            check = cursor.fetchone()
            if check is None:
                error = "Unable to find quiz."
            else:
                cursor.execute(
                "DELETE FROM quizzes WHERE (id=?)", 
                (quiz_id, ))
                
            con.commit()
            cursor.close()      
    else:
        return redirect(url_for('dashboard'))

    if error:
        session['error'] = error
    else:
        session['msg'] = "Quiz delete sucessfully"      

    return redirect(url_for('dashboard'))


# Add Results Controller
@app.route('/results/add', methods = ['POST', 'GET'])
def add_result():
    current_user_id = 0
    error = None
    quiz_id = None
    student_id = None
    score = None

    if 'user_id' in session:
        current_user_id = session['user_id']
    else:
        return redirect(url_for('login')) 

    con = openDbCon()
    cursor = con.cursor()

    # Fetch list of students and quizzes for populating drop-downs
    students_list = list()
    quizzes_list = list()

    # Fetch students
    cursor.execute('SELECT id, firstname, lastname FROM students')
    for student in cursor:
        students_list.append({
            "id" : student[0],
            "firstname" : student[1],
            "lastname" : student[2],
        })

    # Fetch quizzes
    cursor.execute('SELECT id, subject, no_of_questions, date FROM quizzes')
    for quiz in cursor:
        quizzes_list.append({
            "id" : quiz[0],
            "subject" : quiz[1],
            "no_of_questions" : quiz[2],
            "date" : quiz[3],
        })


    if current_user_id != 0 and request.method == 'POST':
        if 'quiz_id' in request.form:
            quiz_id = request.form['quiz_id']
        
        if 'student_id' in request.form:
            student_id = request.form['student_id']

        if 'score' in request.form:
            score = request.form['score']


        if not quiz_id:
            error = 'Select a quiz'
        elif not student_id:
            student_id = 'Select a student'
        elif not score:
            error = 'Score is empty'

        if not error:
            # Check if student already exists
            cursor.execute('SELECT * FROM students WHERE (id=?)', (student_id,))
            check = cursor.fetchone()
            if check is None:
                error = "Unable to find student."
            else:
                # Check if quiz already exists
                cursor.execute('SELECT * FROM quizzes WHERE (id=?)', (quiz_id,))
                check = cursor.fetchone()
                if check is None:
                    error = "Unable to find quiz."
        
        if not error:
            try: 
                score = int(score)
                if score <= 0 or score >= 100:
                    error = "Score should be between 0-100"
            except ValueError:
                error = "Invalid score"

        

        if not error:
            # Insert quiz in DB
            cursor.execute(
            "INSERT INTO results(student_id, quiz_id, score) values (?, ?, ?)", 
            (student_id, quiz_id, score, ))

            con.commit()
            cursor.close()
    else:
        return render_template('form_add_result.html', students_list = students_list, quizzes_list = quizzes_list)

    if error:
        return render_template('form_add_result.html', error = error, students_list = students_list, quizzes_list = quizzes_list)
    else:
        session['msg'] = "Result Added Successfully."
        return redirect('/student/' + str(student_id))


# Delete result Controller
@app.route('/results/delete', methods = ['POST', 'GET'])
def delete_result():
    current_user_id = 0
    error = None

    if 'user_id' in session:
        current_user_id = session['user_id']

    result_id = None

    if current_user_id != 0 and request.method == 'POST':
        if 'id' in request.form:
            result_id = request.form['id']
        

        if not result_id:
            error = 'Error! Unable to delete result.'
        else:
            # Delete quiz in DB
            con = openDbCon()
            cursor = con.cursor()

            # Check if quiz already exists
            cursor.execute('SELECT * FROM results WHERE (id=?)', (result_id,))
            check = cursor.fetchone()
            if check is None:
                error = "Unable to find result."
            else:
                cursor.execute(
                "DELETE FROM results WHERE (id=?)", 
                (result_id, ))
                
            con.commit()
            cursor.close()      
    else:
        return redirect(url_for('dashboard'))

    if error:
        session['error'] = error
    else:
        session['msg'] = "Result delete sucessfully"      

    return redirect(url_for('dashboard'))

# Student Results Controller
@app.route('/student/<id>', methods = ['POST', 'GET'])
def student_results(id):
    current_user_id = 0
    student_id = id
    error = None

    if 'user_id' in session:
        current_user_id = session['user_id']
    else:
        return redirect(url_for('login')) 

    results = list()

    con = openDbCon()
    cursor = con.cursor()

    # Fetch students
    cursor.execute('SELECT results.id, results.student_id, students.firstname, students.lastname, results.score, results.quiz_id, quizzes.subject, quizzes.date FROM results JOIN students ON results.student_id = students.id JOIN quizzes ON quizzes.id = results.quiz_id  WHERE results.student_id = ?', (student_id, ))
    for result in cursor:
        results.append({
            "id" : result[0],
            "student_id" : result[1],
            "firstname" : result[2],
            "lastname" : result[3],
            "score" : result[4],
            "quiz_id" : result[5],
            "subject" : result[6],
            "date" : result[7],
        })

    cursor.close()

    return render_template('results.html', error = error, results = results)



# Student Results Controller
@app.route('/quiz/<id>/results')
def quiz_results(id):
    current_user_id = 0
    quiz_id = id
    error = None

    if 'user_id' in session: # Not for logged in users
        return redirect(url_for('dashboard')) 
        

    results = list()

    con = openDbCon()
    cursor = con.cursor()

    # Fetch students
    cursor.execute('SELECT results.id, results.student_id, results.score, results.quiz_id, quizzes.subject, quizzes.date FROM results JOIN students ON results.student_id = students.id JOIN quizzes ON quizzes.id = results.quiz_id  WHERE results.quiz_id = ?', (quiz_id, ))
    for result in cursor:
        results.append({
            "id" : result[0],
            "student_id" : result[1],
            "score" : result[2],
            "quiz_id" : result[3],
            "subject" : result[4],
            "date" : result[5],
        })

    cursor.close()

    return render_template('quiz_results.html', error = error, results = results)


    

if __name__ == '__main__':
    app.run(debug = True)