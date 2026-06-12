import sqlite3
from datetime import datetime
import hashlib
import os

DB_NAME = "users_data.db"

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, name TEXT, email TEXT, 
        role TEXT, created_at TEXT, question_count INTEGER, status TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, 
        question TEXT, created_at TEXT, doc_chars INTEGER)""")
    
    # کاربر ادمین پیشفرض
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",
                  ('admin', hash_password('123456'), 'مدیر سیستم', 'admin@nus.ac.ir', 'admin', '2024-01-01', 0, 'فعال'))
    conn.commit()
    conn.close()

def verify_user(u, p):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
    row = c.fetchone()
    conn.close()
    if row:
        return True, {"username": row[0], "name": row[2], "role": row[4], "status": row[7]}
    return False, None

def register_user(u, p, n, e):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",
                  (u, hash_password(p), n, e, 'user', datetime.now().date(), 0, 'فعال'))
        conn.commit()
        return True, "ثبت نام موفقیت آمیز بود"
    except: return False, "نام کاربری تکراری است"
    finally: conn.close()

def get_today_question_count(u):
    conn = get_db()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM questions WHERE username=? AND created_at LIKE ?", (u, f"{today}%"))
    count = c.fetchone()[0]
    conn.close()
    return count

def add_question(u, q, chars):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO questions (username, question, created_at, doc_chars) VALUES (?,?,?,?)",
              (u, q, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chars))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, name, email, role, created_at, question_count, status FROM users")
    rows = c.fetchall()
    conn.close()
    return rows
