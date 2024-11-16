import json
from typing import Dict
from google.generativeai import GenerativeModel
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyA7PCrP3WHcAzekLxj_zTScZy29Tom5FvE")

class BackendAgent:
    def __init__(self):
        self.model = GenerativeModel('gemini-pro')
        
        self.system_prompt = """
        You are an AI assistant that converts natural language into database operations.
        Convert user requests into JSON commands with this structure:
        {
            "operation": "create|read|update|delete",
            "table": "table_name",
            "data": {
                "key": "value"
            },
            "condition": {
                "field": "value"  // for update/delete/read operations
            }
        }
        Only respond with valid JSON. No other text.
        """

    def interpret_command(self, user_input: str):
        try:
            response = self.model.generate_content([
                self.system_prompt,
                user_input
            ])
            
            command = json.loads(response.text)
            return {"success": True, "command": command}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ... rest of your BackendAgent class ...

    def explain_action(self, command: Dict) -> str:
        """Generate human-readable explanation of the action"""
        operation = command.get("operation")
        table = command.get("table")
        data = command.get("data", {})
        condition = command.get("condition", {})
        
        if operation == "create":
            return f"Creating new record in {table} with data: {data}"
        elif operation == "read":
            return f"Reading from {table} where {condition}"
        elif operation == "update":
            return f"Updating {table} with {data} where {condition}"
        elif operation == "delete":
            return f"Deleting from {table} where {condition}"
        else:
            return "Unknown operation"