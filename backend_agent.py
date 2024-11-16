import os
from dotenv import load_dotenv
import json
from typing import Dict
import google.generativeai as genai
from google.generativeai import GenerativeModel

load_dotenv()

class BackendAgent:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = GenerativeModel('gemini-pro')
        
        self.system_prompt = """
        You are an AI assistant that converts natural language into database operations.
        Convert user requests into JSON commands with this structure following these examples:

        "create john" →
        {
            "operation": "create",
            "table": "records",
            "data": {
                "value": "john"
            }
        }

        "read" or "show all records" →
        {
            "operation": "read",
            "table": "records"
        }

        "update id 1 to johnson" →
        {
            "operation": "update",
            "table": "records",
            "data": {
                "value": "johnson"
            },
            "condition": {
                "id": "1"
            }
        }

        "delete id 1" →
        {
            "operation": "delete",
            "table": "records",
            "condition": {
                "id": "1"
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

    def explain_action(self, command: Dict) -> str:
        """Generate human-readable explanation of the action"""
        operation = command.get("operation")
        table = command.get("table")
        data = command.get("data", {})
        condition = command.get("condition", {})
        
        if operation == "create":
            return f"Created new record: {data.get('value', '')}"
        elif operation == "read":
            return f"Displaying all records"
        elif operation == "update":
            return f"Updated record ID {condition.get('id', '')} to: {data.get('value', '')}"
        elif operation == "delete":
            return f"Deleted record ID {condition.get('id', '')}"
        else:
            return "Unknown operation"