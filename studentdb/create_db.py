import sqlite3

con = sqlite3.connect("students.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll TEXT UNIQUE,
    age INTEGER,
    course TEXT,
    cgpa REAL,
    photo TEXT
)
""")

con.commit()
con.close()

print("Base students table created successfully!")