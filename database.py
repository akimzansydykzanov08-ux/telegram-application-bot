import sqlite3

def init_db():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT ,
    user_id INTEGER,
    name TEXT,
    phone TEXT,
    comment TEXT)""")

    conn.commit()
    conn.close()

def add_applications(user_id:int , name: str, phone: str, comment:str):
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO applications (user_id, name, phone, comment) 
    VALUES (?, ?, ?, ?) 
    """, (user_id, name, phone, comment))

    conn.commit()
    conn.close()

def delete_application_by_id(app_id:int):
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()

def get_all_applications():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, user_id,  name, phone, comment FROM applications""")

    rows = cursor.fetchall()

    conn.close()
    return rows




