from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'million-secret'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            session['user'] = user[1]
            return redirect('/dashboard')
        flash("Invalid credentials")
    return render_template('elite_login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect('/login')
    return render_template('elite_signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template('elite_dashboard.html', employees=employees, user=session['user'])

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        cursor.execute("INSERT INTO employees (name, position, department) VALUES (%s, %s, %s)", (name, position, department))
        db.commit()
        return redirect('/dashboard')
    return render_template('elite_add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        cursor.execute("UPDATE employees SET name=%s, position=%s, department=%s WHERE id=%s", (name, position, department, id))
        db.commit()
        return redirect('/dashboard')
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()
    return render_template('elite_edit_employee.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
