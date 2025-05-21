import json
from pathlib import Path
class UserRegistration:
    def __init__(self, filepath='users.json'):
        self.filepath = Path(filepath)
        self.users = self._load()

    def _load(self):
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.users, f, indent=4)

    def get_user(self, username):
        return self.users.get(username)

    def add_user(self, username, password):
        self.users[username] = {
            "password": password
        }
        self._save()