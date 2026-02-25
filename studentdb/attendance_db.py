import sqlite3

con = sqlite3.connect("students.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

con.commit()
con.close()

print("Attendance table created!")