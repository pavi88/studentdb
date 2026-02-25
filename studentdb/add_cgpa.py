import sqlite3

con = sqlite3.connect("students.db")
cur = con.cursor()

try:
    cur.execute("ALTER TABLE students ADD COLUMN cgpa REAL")
    print("CGPA column added!")
except Exception as e:
    print("Already exists or error:", e)

con.commit()
con.close()