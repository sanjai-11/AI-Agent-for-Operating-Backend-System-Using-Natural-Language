import json
from datetime import datetime
from typing import Dict, Any, Optional

class Database:
    def __init__(self, filename: str = 'database.json'):
        self.filename = filename
        self.load_database()

    def load_database(self):
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
            if not self.data:
                self.data = {'users': {}, 'records': {}}
                self.save_database()
        except FileNotFoundError:
            self.data = {'users': {}, 'records': {}}
            self.save_database()

    def save_database(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)

    def create_user(self, user_id: int, email: str, username: str, password_hash: str) -> Dict[str, Any]:
        self.data['users'][str(user_id)] = {
            'email': email,
            'username': username,
            'password_hash': password_hash
        }
        self.save_database()
        return {'success': True}

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if str(user_id) in self.data['users']:
            return self.data['users'][str(user_id)]
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for user in self.data['users'].values():
            if user['email'] == email:
                return user
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        for user in self.data['users'].values():
            if user['username'] == username:
                return user
        return None

    def get_next_user_id(self) -> int:
        if not self.data['users']:
            return 1
        return max(int(user_id) for user_id in self.data['users']) + 1

    def get_next_record_id(self, user_id: int) -> int:
        if str(user_id) not in self.data['records'] or not self.data['records'][str(user_id)]:
            return 1
        return max(record['id'] for record in self.data['records'][str(user_id)]) + 1

    def create_record(self, user_id: int, data: Dict) -> Dict[str, Any]:
        if str(user_id) not in self.data['records']:
            self.data['records'][str(user_id)] = []

        record = {
            "id": self.get_next_record_id(user_id),
            "value": data.get("value"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        self.data['records'][str(user_id)].append(record)
        self.save_database()

        return {"success": True, "data": record}

    def read_records(self, user_id: int) -> Dict[str, Any]:
        if str(user_id) not in self.data['records'] or not self.data['records'][str(user_id)]:
            return {"success": False, "error": "No records found"}
        return {"success": True, "data": self.data['records'][str(user_id)]}

    def update_record(self, user_id: int, data: Dict, condition: Dict) -> Dict[str, Any]:
        if str(user_id) not in self.data['records']:
            return {"success": False, "error": "No records found"}

        updated_record = None
        for record in self.data['records'][str(user_id)]:
            if str(record['id']) == str(condition['id']):
                record['value'] = data['value']
                record['updated_at'] = datetime.now()
                updated_record = record
                break

        if not updated_record:
            return {"success": False, "error": f"Record with ID {condition['id']} not found"}

        self.save_database()
        return {"success": True, "data": updated_record}

    def delete_record(self, user_id: int, condition: Dict) -> Dict[str, Any]:
        if str(user_id) not in self.data['records']:
            return {"success": False, "error": "No records found"}

        original_length = len(self.data['records'][str(user_id)])
        self.data['records'][str(user_id)] = [
            record for record in self.data['records'][str(user_id)]
            if str(record['id']) != str(condition['id'])
        ]

        if len(self.data['records'][str(user_id)]) == original_length:
            return {"success": False, "error": f"Record with ID {condition['id']} not found"}

        self.save_database()
        return {"success": True, "message": f"Record with ID {condition['id']} deleted"}