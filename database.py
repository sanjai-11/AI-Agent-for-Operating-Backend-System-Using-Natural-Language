import json
from datetime import datetime
from typing import Dict, Any

class Database:
    def __init__(self, filename: str = 'database.json'):
        self.filename = filename
        self.load_database()

    def load_database(self):
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
            if not self.data:
                self.data = {"records": []}
                self.save_database()
        except FileNotFoundError:
            self.data = {"records": []}
            self.save_database()

    def save_database(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)

    def get_next_id(self, table: str) -> int:
        if not self.data[table]:
            return 1
        return max(record['id'] for record in self.data[table]) + 1

    def create(self, table: str, data: Dict) -> Dict[str, Any]:
        if table not in self.data:
            self.data[table] = []
        
        record = {
            "id": self.get_next_id(table),
            "value": data.get("value"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.data[table].append(record)
        self.save_database()
        
        return {"success": True, "data": record}

    def read(self, table: str, condition: Dict = None) -> Dict[str, Any]:
        if table not in self.data:
            return {"success": False, "error": "No records found"}
        
        return {"success": True, "data": self.data[table]}

    def update(self, table: str, data: Dict, condition: Dict) -> Dict[str, Any]:
        if table not in self.data:
            return {"success": False, "error": "No records found"}
            
        updated_record = None
        for record in self.data[table]:
            if str(record['id']) == str(condition['id']):
                record['value'] = data['value']
                record['updated_at'] = datetime.now()
                updated_record = record
                break
                
        if not updated_record:
            return {"success": False, "error": f"Record with ID {condition['id']} not found"}
            
        self.save_database()
        return {"success": True, "data": updated_record}

    def delete(self, table: str, condition: Dict) -> Dict[str, Any]:
        if table not in self.data:
            return {"success": False, "error": "No records found"}
            
        original_length = len(self.data[table])
        self.data[table] = [
            record for record in self.data[table]
            if str(record['id']) != str(condition['id'])
        ]
        
        if len(self.data[table]) == original_length:
            return {"success": False, "error": f"Record with ID {condition['id']} not found"}
            
        self.save_database()
        return {"success": True, "message": f"Record with ID {condition['id']} deleted"}