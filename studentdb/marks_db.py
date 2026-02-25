import sqlite3

con = sqlite3.connect("students.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS marks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    marks INTEGER,
    total_marks INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

con.commit()
con.close()

print("Marks table created!")