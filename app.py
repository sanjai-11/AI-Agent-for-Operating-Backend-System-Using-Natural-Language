from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from backend_agent import BackendAgent
from database import Database
from user import User
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
backend_agent = BackendAgent()
database = Database()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('index'))
    else:
        return render_template('home.html')  # Create a home.html template

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user = User.create(email, username, password)
        if user:
            database.create_user(user.id, user.email, user.username, user.password_hash)
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Email or username already taken.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        print(f"Attempting to authenticate user: {identifier}")
        user = User.authenticate(identifier, password)
        if user:
            session['user_id'] = user.id
            print(f"User {user.username} logged in successfully")
            return redirect(url_for('index'))
        else:
            flash('Invalid email/username or password.', 'error')
            print("Login failed")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/index')
def index():
    user = User.get_current_user()
    if user:
        result = database.read_records(user.id)
        if result['success']:
            return render_template('index.html', records=result['data'], username=user.username)
        else:
            flash(result['error'], 'error')
            return render_template('index.html', records=[], username=user.username)
    else:
        flash('Please log in to access the index page.', 'error')
        return redirect(url_for('login'))

@app.route('/execute', methods=['POST'])
def execute_command():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_id = session['user_id']
    user_input = request.form['command']
    interpretation = backend_agent.interpret_command(user_input)

    if not interpretation['success']:
        return jsonify({"error": interpretation['error']}), 400

    command = interpretation['command']

    if "operations" in command:
        results = []
        for op in command["operations"]:
            result = execute_single_operation(op, user_id)
            if not result['success']:
                return jsonify({"error": result['error']}), 500
            results.append(result)

        return jsonify({
            "success": True,
            "message": "Multiple operations completed successfully",
            "data": results
        })

    result = execute_single_operation(command, user_id)
    if result['success']:
        return jsonify({
            "success": True,
            "message": backend_agent.explain_action(command),
            "data": result.get('data', result.get('records', []))
        })
    else:
        return jsonify({"success": False, "error": result['error']}), 500

def execute_single_operation(command, user_id):
    operation = command['operation']
    data = command.get('data', {})
    condition = command.get('condition', {})

    if operation == 'create':
        result = database.create_record(user_id, data)
    elif operation == 'read':
        result = database.read_records(user_id)
    elif operation == 'update':
        result = database.update_record(user_id, data, condition)
    elif operation == 'delete':
        result = database.delete_record(user_id, condition)
    else:
        return {"success": False, "error": "Unknown operation"}

    return result

if __name__ == '__main__':
    app.run(debug=True)