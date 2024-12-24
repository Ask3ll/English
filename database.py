import sqlite3
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
    def exec(self, wte, commit=False):
        self.cursor.execute(wte)
        if commit:
            self.conn.commit()
    def close(self):
        self.cursor.close()
        self.conn.close()
    def all(self):
        return self.cursor.fetchall()
    def one(self):
        return self.cursor.fetchone()
    def create_table(self, name):
        self.exec(f"CREATE TABLE {name} (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, correct INTEGER, incorrect INTEGER, total INTEGER)")

if __name__ == "__main__":
    db = Database()
    db.exec(f"DELETE FROM questions", True)
