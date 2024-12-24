import sqlite3
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("database.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()
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
    def create_table(self):
        self.exec("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, correct INTEGER, incorrect INTEGER, total INTEGER)")
        self.exec("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, answer TEXT, translate TEXT)")
if __name__ == "__main__":
    db = Database()
    db.exec(f"DELETE FROM questions", True)
