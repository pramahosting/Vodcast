import os
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "data/users.db"  # example path

def authenticate_user(email, password):
    email = email.lower().strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if user:
        stored_password = user[3]  # assuming password is 4th column (index 3)
        hashed_input_pw = hash_password(password)
        if stored_password == hashed_input_pw:
            user_data = {
                "email": user[1],         # email
                "name": user[2],          # name
                "company_name": user[4],  # company_name
                "is_admin": bool(user[12]) if len(user) > 12 else False,
                "is_active": user[5],     # is_active
            }
            if user_data["is_active"] == 1:
                return True, user_data
            else:
                return False, "Account deactivated"
    return False, "Invalid credentials"


def create_user_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            password TEXT,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            last_login TEXT
        )
    """)
    conn.commit()
    conn.close()

def migrate_user_table():
    """
    Add missing columns to users table if they don't exist
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    columns_to_add = [
        ("company_name", "TEXT"),
        ("company_email", "TEXT"),
        ("job_title", "TEXT"),
        ("company_website", "TEXT"),
        ("contact_number", "TEXT"),
        ("country", "TEXT"),
        ("state", "TEXT"),
        ("address", "TEXT"),
    ]

    for column, dtype in columns_to_add:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {column} {dtype}")
        except sqlite3.OperationalError:
            # Column already exists
            pass

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(email, name, password, company_name="", company_email="", job_title="", company_website="",
                contact_number="", country="", state="", address="", is_admin=False):
    email = email.lower().strip()  # Normalize email here
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        c.execute("""
            INSERT INTO users (email, name, password, company_name, company_email, job_title, company_website,
                               contact_number, country, state, address, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, name, hashed_pw, company_name, company_email, job_title, company_website,
              contact_number, country, state, address, int(is_admin), datetime.now().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    email = email.lower().strip()  # Normalize email here
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed_pw))
    user = c.fetchone()
    if user:
        c.execute("SELECT is_active, is_admin FROM users WHERE email=?", (email,))
        status = c.fetchone()
        if status is None:
            conn.close()
            return False, "User not found"
        is_active, is_admin = status
        if is_active == 1:
            c.execute("UPDATE users SET last_login=? WHERE email=?", (datetime.now().isoformat(), email))
            conn.commit()
            conn.close()
            return True, bool(is_admin)
        else:
            conn.close()
            return False, "Account deactivated"
    conn.close()
    return False, "Invalid credentials"

def deactivate_user(email):
    email = email.lower().strip()  # Normalize email here
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=0 WHERE email=?", (email,))
    conn.commit()
    conn.close()

def activate_user(email):
    email = email.lower().strip()  # Normalize email here
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    email = email.lower().strip()  # Normalize email here
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return {"name": row[0]} if row else {}

def list_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT email, name, company_name, is_admin, is_active, created_at, last_login 
        FROM users
    """)
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    create_user_table()
    migrate_user_table()
    print("Database ready.")
