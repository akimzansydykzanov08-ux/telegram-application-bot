import sqlite3

def init_db():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT ,
    name TEXT,
    phone TEXT,
    comment TEXT)""")

    conn.commit()
    conn.close()

def add_applications(name: str, phone: str, comment:str):
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO applications (name, phone, comment) 
    VALUES (?, ?, ?) 
    """, (name, phone, comment))

    conn.commit()
    conn.close()

def get_all_applications():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, phone, comment FROM applications""")

    rows = cursor.fetchall()

    conn.close()
    return rows




