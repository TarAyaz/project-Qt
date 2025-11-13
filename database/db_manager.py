import sqlite3
from pathlib import Path
from datetime import datetime


class DatabaseManager:
    # // === Создание базы данных ===
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = Path(__file__).parent / "project.db"
        else:
            self.db_path = Path(db_path)
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER,
                    due_date TEXT,
                    category TEXT,
                    completed INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,
                    time TEXT,
                    color TEXT,
                    is_recurring INTEGER,
                    event_type TEXT DEFAULT 'default_event'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

    # === Задачи ===
    def save_tasks(self, tasks):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tasks")
            for t in tasks:
                conn.execute(
                    """
                    INSERT INTO tasks (title, description, priority, due_date, category, completed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        t["title"],
                        t["description"],
                        t["priority"],
                        t["due_date"],
                        t["category"],
                        int(t["completed"]),
                    ),
                )

    def load_tasks(self):
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT title, description, priority, due_date, category, completed
                FROM tasks
            """).fetchall()
            return [
                {
                    "title": r[0],
                    "description": r[1],
                    "priority": r[2],
                    "due_date": r[3],
                    "category": r[4],
                    "completed": bool(r[5]),
                }
                for r in rows
            ]

    # === События ===
    def save_events(self, events):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM events")
            for e in events:
                conn.execute(
                    """
                    INSERT INTO events (title, description, date, time, color, is_recurring, event_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        e["title"],
                        e["description"],
                        e["date"],
                        e["time"],
                        e["color"],
                        int(e["is_recurring"]),
                        e.get("type", "default_event"),
                    ),
                )

    def load_events(self):
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT title, description, date, time, color, is_recurring, event_type
                FROM events
            """).fetchall()
            return [
                {
                    "title": r[0],
                    "description": r[1],
                    "date": r[2],
                    "time": r[3],
                    "color": r[4],
                    "is_recurring": bool(r[5]),
                    "type": r[6],
                }
                for r in rows
            ]

    # === Заметки ===
    def save_notes(self, notes):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM notes")
            for n in notes:
                created = n.get("created_at") or datetime.now().strftime("%Y-%m-%d")
                updated = datetime.now().strftime("%Y-%m-%d %H:%M")
                conn.execute(
                    """
                    INSERT INTO notes (title, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (n["title"], n["content"], created, updated),
                )

    def load_notes(self):
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT title, content, created_at
                FROM notes
            """).fetchall()
            return [{"title": r[0], "content": r[1], "created_at": r[2]} for r in rows]
