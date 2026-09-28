import sqlite3
import hashlib
from datetime import datetime

from constants import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS trainers (
    user_id INTEGER PRIMARY KEY,
    specialization TEXT,
    experience INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS athletes (
    user_id INTEGER PRIMARY KEY,
    birth_date TEXT,
    goal TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    muscle_group TEXT,
    video_url TEXT,
    created_by INTEGER
);

CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_id INTEGER,
    athlete_id INTEGER,
    title TEXT NOT NULL,
    date TEXT,
    status TEXT DEFAULT 'Черновик',
    comment TEXT
);

CREATE TABLE IF NOT EXISTS training_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    training_id INTEGER,
    exercise_id INTEGER,
    sets INTEGER,
    reps INTEGER,
    weight REAL,
    duration INTEGER,
    order_num INTEGER,
    completed INTEGER DEFAULT 0,
    FOREIGN KEY (training_id) REFERENCES trainings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progress_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER,
    exercise_id INTEGER,
    date TEXT,
    weight REAL,
    reps INTEGER,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    training_id INTEGER,
    message TEXT,
    date TEXT,
    is_read INTEGER DEFAULT 0
);
"""


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)

        if conn.execute("SELECT 1 FROM users WHERE login='admin'").fetchone() is None:
            conn.execute(
                "INSERT INTO users (login, password_hash, role, full_name, email, phone) "
                "VALUES (?,?,?,?,?,?)",
                ('admin', hash_password('admin'), 'admin',
                 'Администратор системы', 'admin@local', '')
            )

        if conn.execute("SELECT 1 FROM users WHERE login='trainer'").fetchone() is None:
            conn.execute(
                "INSERT INTO users (login, password_hash, role, full_name, email, phone) "
                "VALUES (?,?,?,?,?,?)",
                ('trainer', hash_password('trainer'), 'trainer',
                 'Иванов Иван Иванович', 'trainer@mail.ru', '+7(900)000-00-01')
            )
            tid = conn.execute("SELECT id FROM users WHERE login='trainer'").fetchone()['id']
            conn.execute(
                "INSERT INTO trainers (user_id, specialization, experience) VALUES (?,?,?)",
                (tid, 'Силовой тренинг', 5)
            )

        if conn.execute("SELECT 1 FROM users WHERE login='athlete'").fetchone() is None:
            conn.execute(
                "INSERT INTO users (login, password_hash, role, full_name, email, phone) "
                "VALUES (?,?,?,?,?,?)",
                ('athlete', hash_password('athlete'), 'athlete',
                 'Петров Пётр Петрович', 'athlete@mail.ru', '+7(900)000-00-02')
            )
            aid = conn.execute("SELECT id FROM users WHERE login='athlete'").fetchone()['id']
            conn.execute(
                "INSERT INTO athletes (user_id, birth_date, goal) VALUES (?,?,?)",
                (aid, '1995-05-15', 'Набор мышечной массы')
            )

        cnt = conn.execute("SELECT COUNT(*) AS c FROM exercises").fetchone()['c']
        if cnt == 0:
            trainer_id = conn.execute(
                "SELECT id FROM users WHERE login='trainer'"
            ).fetchone()['id']
            demo = [
                ('Жим штанги лёжа',      'Базовое упражнение на грудные мышцы', 'Грудь',  ''),
                ('Приседания со штангой','Базовое упражнение на ноги',          'Ноги',   ''),
                ('Становая тяга',        'Базовое упражнение на спину',         'Спина',  ''),
                ('Подтягивания',         'Упражнение на широчайшие мышцы спины','Спина',  ''),
                ('Отжимания на брусьях', 'Упражнение на трицепс и грудь',       'Грудь',  ''),
                ('Жим гантелей сидя',    'Упражнение на плечи',                 'Плечи',  ''),
                ('Сгибания рук со штангой', 'Упражнение на бицепс',             'Руки',   ''),
                ('Разгибания рук на блоке', 'Упражнение на трицепс',            'Руки',   ''),
                ('Планка',               'Статическое упражнение на пресс',     'Пресс',  ''),
                ('Скручивания',          'Упражнение на пресс',                 'Пресс',  ''),
            ]
            for name, desc, mg, url in demo:
                conn.execute(
                    "INSERT INTO exercises (name, description, muscle_group, video_url, created_by) "
                    "VALUES (?,?,?,?,?)",
                    (name, desc, mg, url, trainer_id)
                )
        conn.commit()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    conn = connect()
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()


def fetch_all(sql, params=()):
    conn = connect()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def execute(sql, params=()):
    conn = connect()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def notify(user_id: int, message: str, training_id=None) -> None:
    execute(
        "INSERT INTO notifications (user_id, training_id, message, date, is_read) "
        "VALUES (?,?,?,?,0)",
        (user_id, training_id, message, datetime.now().strftime('%Y-%m-%d %H:%M'))
    )
