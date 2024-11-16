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
    
    # Handle multiple operations
    if "operations" in command:
        results = []
        for op in command["operations"]:
            result = execute_single_operation(op)
            if not result['success']:
                return jsonify({"error": f"Operation failed: {result['error']}"})
            results.append(result)
        
        return jsonify({
            "message": "Multiple operations completed successfully",
            "data": results
        })
    
    # Handle single operation
    return execute_single_operation(command)

def execute_single_operation(command):
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
        return {"success": False, "error": "Unknown operation"}
    
    if result['success']:
        explanation = backend_agent.explain_action(command)
        return {
            "success": True,
            "message": explanation,
            "data": result.get('data') or result.get('message')
        }
    else:
        return {"success": False, "error": result['error']}

if __name__ == '__main__':
    app.run(debug=True)