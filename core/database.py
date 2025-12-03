import sqlite3
from pathlib import Path

DB_PATH = Path("quests.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Основная таблица квестов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            difficulty TEXT CHECK(difficulty IN ('Лёгкий', 'Средний', 'Сложный', 'Олимпийский')),
            reward INTEGER,
            description TEXT,
            deadline TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица версий (история изменений)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quest_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER NOT NULL,
            title TEXT,
            difficulty TEXT,
            reward INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def save_quest(title, difficulty, reward, description, deadline):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO quests (title, difficulty, reward, description, deadline)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                difficulty = excluded.difficulty,
                reward = excluded.reward,
                description = excluded.description,
                deadline = excluded.deadline
        """, (title, difficulty, reward, description, deadline))

        quest_id = cur.lastrowid
        if not quest_id:
            cur.execute("SELECT id FROM quests WHERE title = ?", (title,))
            quest_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO quest_versions (quest_id, title, difficulty, reward, description)
            VALUES (?, ?, ?, ?, ?)
        """, (quest_id, title, difficulty, reward, description))

        conn.commit()
        return quest_id
    finally:
        conn.close()


def get_quest_by_id(quest_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, difficulty, reward, description, deadline
        FROM quests WHERE id = ?
    """, (quest_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "title": row[1],
            "difficulty": row[2],
            "reward": row[3],
            "description": row[4],
            "deadline": row[5]
        }
    return None