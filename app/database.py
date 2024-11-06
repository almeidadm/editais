import sqlite3
import json


class Database:
    def __init__(self, db_name="announcements.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.connection as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS announcements (
                id TEXT PRIMARY KEY,
                title TEXT,
                fontes TEXT,
                locais TEXT
            )''')

    def save_announcement(self, data: dict) -> bool:
        with self.connection as conn:
            try:
                conn.execute(
                    '''INSERT INTO announcements (id, title, fontes, locais) VALUES (?, ?, ?, ?)''',
                    (data['id'], data['nome'], json.dumps(data['fontes']), json.dumps(data['locais']))
                )
                return True  # Indica que é um novo edital
            except sqlite3.IntegrityError:
                return False  # Edital já existente


if __name__ == "__main__":
    db = Database()
