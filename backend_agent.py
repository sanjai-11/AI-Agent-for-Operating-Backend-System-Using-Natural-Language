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

        Single Operations:
        "create john" →
        {
            "operation": "create",
            "table": "records",
            "data": {
                "value": "john"
            }
        }

        "read" or "show all records" or "display records" →
        {
            "operation": "read",
            "table": "records"
        }

        "update id 1 to johnson" or "change id 1 to johnson" →
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

        "delete id 1" or "remove id 1" →
        {
            "operation": "delete",
            "table": "records",
            "condition": {
                "id": "1"
            }
        }

        Error Cases:
        If invalid command or missing information →
        {
            "operation": "error",
            "message": "Invalid command. Please provide a valid operation (create/read/update/delete)"
        }

        If missing ID for update/delete →
        {
            "operation": "error",
            "message": "Please provide an ID for update/delete operation"
        }

        If missing value for create/update →
        {
            "operation": "error",
            "message": "Please provide a value for create/update operation"
        }

        Multiple Operations (preserve order):
        "create john, update id 1 to johnson, delete id 1" →
        {
            "operations": [
                {
                    "operation": "create",
                    "table": "records",
                    "data": {
                        "value": "john"
                    }
                },
                {
                    "operation": "update",
                    "table": "records",
                    "data": {
                        "value": "johnson"
                    },
                    "condition": {
                        "id": "1"
                    }
                },
                {
                    "operation": "delete",
                    "table": "records",
                    "condition": {
                        "id": "1"
                    }
                }
            ]
        }

        Keywords to identify operations:
        - Create: "create", "add", "new", "insert"
        - Read: "read", "show", "display", "get", "list", "view"
        - Update: "update", "change", "modify", "set"
        - Delete: "delete", "remove", "clear"

        Only respond with valid JSON. No other text.
        For multiple operations, maintain the exact order as given in the input.
        Validate each operation for required fields before processing.
        """
        
    def interpret_command(self, user_input: str):
        try:
            response = self.model.generate_content([
                self.system_prompt,
                user_input
            ])
            
            # Check if the response is valid JSON
            try:
                command = json.loads(response.text)
            except json.JSONDecodeError:
                return {"success": False, "error": f"Invalid response from AI model: {response.text[:100]}..."}
            
            # Check if it's an error response
            if command.get("operation") == "error":
                return {"success": False, "error": command["message"]}
                
            # Check if it's a multiple operations command
            if "operations" in command:
                # Validate each operation in the sequence
                for op in command["operations"]:
                    if op["operation"] == "create" and "value" not in op.get("data", {}):
                        return {"success": False, "error": "Missing value for create operation"}
                    if op["operation"] in ["update", "delete"] and "id" not in op.get("condition", {}):
                        return {"success": False, "error": f"Missing ID for {op['operation']} operation"}
                    if op["operation"] == "update" and "value" not in op.get("data", {}):
                        return {"success": False, "error": "Missing value for update operation"}
            
            return {"success": True, "command": command}
            
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}
        
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