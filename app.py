# from flask import Flask, render_template, request, jsonify
# import os
# from dotenv import load_dotenv

# # Debug prints
# print("Starting application...")

# app = Flask(__name__)
# print(f"Template folder path: {app.template_folder}")

# @app.route('/')
# def home():
#     print("Home route accessed")
#     try:
#         return render_template('index.html')
#     except Exception as e:
#         print(f"Error rendering template: {e}")
#         return str(e)

# if __name__ == '__main__':
#     print("Starting Flask server...")
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
from backend_agent import BackendAgent
from database import Database
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
backend_agent = BackendAgent()
database = Database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    user_input = request.form['command']
    interpretation = backend_agent.interpret_command(user_input)
    
    if not interpretation['success']:
        return jsonify({"error": interpretation['error']})
    
    command = interpretation['command']
    explanation = backend_agent.explain_action(command)
    
    operation = command['operation']
    table = command['table']
    data = command.get('data', {})
    condition = command.get('condition', {})
    
    if operation == 'create':
        result = database.create(table, data)
    elif operation == 'read':
        result = database.read(table, condition)
    elif operation == 'update':
        result = database.update(table, data, condition)
    elif operation == 'delete':
        result = database.delete(table, condition)
    else:
        return jsonify({"error": "Unknown operation"})
    
    if result['success']:
        return jsonify({
            "message": explanation,
            "data": result.get('data') or result.get('message')
        })
    else:
        return jsonify({"error": result['error']})

if __name__ == '__main__':
    app.run(debug=True)