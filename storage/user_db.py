import hashlib
import hmac
import os
import secrets
import sqlite3

DB_NAME = "loan.db"
HASH_PREFIX = "pbkdf2_sha256"


def infer_role(email: str, user_count: int) -> str:
    local_part = email.split("@", 1)[0].lower()

    if user_count == 0:
        return "admin"
    if "admin" in local_part:
        return "admin"
    if "review" in local_part or "ops" in local_part:
        return "reviewer"
    return "customer"


def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'customer'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'customer'")

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )
    return f"{HASH_PREFIX}${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    if not stored_password:
        return False

    if not stored_password.startswith(f"{HASH_PREFIX}$"):
        return hmac.compare_digest(password, stored_password)

    _, salt_hex, password_hash_hex = stored_password.split("$", 2)
    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        100000
    ).hex()
    return hmac.compare_digest(computed_hash, password_hash_hex)


def create_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    role = infer_role(email, user_count)

    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, hash_password(password), role)
    )

    conn.commit()
    conn.close()


def get_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, password, role FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    if not user or not verify_password(password, user[2]):
        conn.close()
        return None

    if not user[2].startswith(f"{HASH_PREFIX}$"):
        cursor.execute(
            "UPDATE users SET password=? WHERE id=?",
            (hash_password(password), user[0])
        )
        conn.commit()

    conn.close()

    return user[0], user[1], user[3]


def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, role FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def create_session(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    session_token = secrets.token_urlsafe(32)

    cursor.execute(
        "INSERT INTO user_sessions (user_id, session_token) VALUES (?, ?)",
        (user_id, session_token)
    )

    conn.commit()
    conn.close()
    return session_token


def get_user_by_session(session_token):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT users.id, users.name, users.email, users.role
        FROM user_sessions
        JOIN users ON users.id = user_sessions.user_id
        WHERE user_sessions.session_token = ?
        ORDER BY user_sessions.id DESC
        LIMIT 1
        """,
        (session_token,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def delete_session(session_token):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_sessions WHERE session_token = ?",
        (session_token,)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0
