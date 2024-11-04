import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

def add_user(user_id):
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

# Session

def get_sessions(user_id):
    cursor.execute("SELECT session_names FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    try:
        return result[0]
    except:
        return result

def add_sessions(user_id, sessions:str):
    cursor.execute("SELECT session_names FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    current_sessions = result[0] if result and result[0] else ""

    updates_sessions = f"{current_sessions}, {sessions}".strip(", ")

    cursor.execute("UPDATE users SET session_names = ? WHERE user_id = ?", (updates_sessions, user_id))
    conn.commit()

# Proxy

def get_proxy(user_id):
    cursor.execute("SELECT proxy_list FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    try:
        return result[0]
    except:
        return result

def add_proxy(user_id, proxy:str):
    cursor.execute("SELECT proxy_list FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    current_proxy = result[0] if result and result[0] else ""

    updates_proxy_list = f"{current_proxy}, {proxy}".strip(", ")

    cursor.execute("UPDATE users SET proxy_list = ? WHERE user_id = ?", (updates_proxy_list, user_id))
    conn.commit()


