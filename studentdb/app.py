import os
import sqlite3
from flask import Flask, render_template, request, redirect, flash, send_file
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "abc123"

# Upload folder for photos
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------
# ADD STUDENT
# ---------------------------------------------------------
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        age = request.form["age"]
        course = request.form["course"]
        cgpa = request.form["cgpa"]

        # Photo upload
        photo_file = request.files["photo"]
        photo_filename = None

        if photo_file and photo_file.filename != "":
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            photo_file.save(photo_path)

        con = sqlite3.connect("students.db")
        cur = con.cursor()

        cur.execute("""
            INSERT INTO students(name, roll, age, course, cgpa, photo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, roll, age, course, cgpa, photo_filename))

        con.commit()
        con.close()

        flash("Student Added Successfully!")
        return redirect("/view")

    return render_template("add.html")


# ---------------------------------------------------------
# VIEW STUDENTS
# ---------------------------------------------------------
@app.route("/view")
def view_students():
    con = sqlite3.connect("students.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM students")
    data = cur.fetchall()

    con.close()
    return render_template("view.html", students=data)


# ---------------------------------------------------------
# UPDATE STUDENT
# ---------------------------------------------------------
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_student(id):

    con = sqlite3.connect("students.db")
    cur = con.cursor()

    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        age = request.form["age"]
        course = request.form["course"]
        cgpa = request.form["cgpa"]

        # Handle new photo
        photo_file = request.files["photo"]
        if photo_file and photo_file.filename != "":
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            photo_file.save(photo_path)

            cur.execute("""
                UPDATE students SET name=?, roll=?, age=?, course=?, cgpa=?, photo=? WHERE id=?
            """, (name, roll, age, course, cgpa, photo_filename, id))

        else:
            cur.execute("""
                UPDATE students SET name=?, roll=?, age=?, course=?, cgpa=? WHERE id=?
            """, (name, roll, age, course, cgpa, id))

        con.commit()
        con.close()

        flash("Student Updated Successfully!")
        return redirect("/view")

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    con.close()

    return render_template("update.html", student=student)


# ---------------------------------------------------------
# DELETE STUDENT
# ---------------------------------------------------------
@app.route("/delete/<int:id>")
def delete_student(id):
    con = sqlite3.connect("students.db")
    cur = con.cursor()

    cur.execute("DELETE FROM students WHERE id=?", (id,))
    con.commit()
    con.close()

    flash("Student Deleted Successfully!")
    return redirect("/view")


# ---------------------------------------------------------
# SEARCH STUDENT
# ---------------------------------------------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        text = request.form["search"]

        con = sqlite3.connect("students.db")
        cur = con.cursor()

        cur.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ? OR course LIKE ?
        """, ('%' + text + '%', '%' + text + '%', '%' + text + '%'))

        data = cur.fetchall()
        con.close()

        return render_template("view.html", students=data)

    return render_template("search.html")


# ---------------------------------------------------------
# ATTENDANCE MODULE
# ---------------------------------------------------------
@app.route("/attendance/<int:id>", methods=["GET", "POST"])
def attendance(id):
    if request.method == "POST":
        date = request.form["date"]
        status = request.form["status"]

        con = sqlite3.connect("students.db")
        cur = con.cursor()

        cur.execute("""
            INSERT INTO attendance(student_id, date, status)
            VALUES(?,?,?)
        """, (id, date, status))

        con.commit()
        con.close()

        flash("Attendance Marked!")
        return redirect(f"/attendance/{id}")

    con = sqlite3.connect("students.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM attendance WHERE student_id=?", (id,))
    records = cur.fetchall()

    cur.execute("SELECT name FROM students WHERE id=?", (id,))
    student = cur.fetchone()

    con.close()

    return render_template("attendance.html", records=records, student=student, sid=id)


# ---------------------------------------------------------
# MARKS MODULE
# ---------------------------------------------------------
@app.route("/marks/<int:id>", methods=["GET", "POST"])
def marks(id):
    if request.method == "POST":
        subject = request.form["subject"]
        marks = request.form["marks"]
        total = request.form["total"]

        con = sqlite3.connect("students.db")
        cur = con.cursor()

        cur.execute("""
            INSERT INTO marks(student_id, subject, marks, total_marks)
            VALUES (?,?,?,?)
        """, (id, subject, marks, total))

        con.commit()
        con.close()

        flash("Marks Added!")
        return redirect(f"/marks/{id}")

    con = sqlite3.connect("students.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM marks WHERE student_id=?", (id,))
    records = cur.fetchall()

    cur.execute("SELECT name FROM students WHERE id=?", (id,))
    student = cur.fetchone()

    con.close()

    return render_template("marks.html", records=records, student=student, sid=id)


# ---------------------------------------------------------
# DASHBOARD (Charts Page)
# ---------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    con = sqlite3.connect("students.db")
    cur = con.cursor()

    cur.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
    course_data = cur.fetchall()

    cur.execute("SELECT cgpa FROM students")
    cgpas = [row[0] for row in cur.fetchall()]

    con.close()

    return render_template("dashboard.html",
                           course_data=course_data,
                           cgpas=cgpas)


# ---------------------------------------------------------
# PDF REPORT CARD (FINAL & UPGRADED)
# ---------------------------------------------------------
@app.route("/report/<int:id>")
def report(id):
    pdf_path = f"report_{id}.pdf"

    con = sqlite3.connect("students.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    s = cur.fetchone()

    cur.execute("SELECT subject, marks, total_marks FROM marks WHERE student_id=?", (id,))
    marks = cur.fetchall()

    con.close()

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 22)
    c.drawString(180, 770, "STUDENT REPORT CARD")

    if s[6]:
        try:
            c.drawImage(
                f"static/uploads/{s[6]}",
                450, 640, width=100, height=120,
                preserveAspectRatio=True, mask="auto"
            )
        except:
            pass

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 700, "Student Details:")

    c.setFont("Helvetica", 12)
    c.drawString(50, 680, f"Name: {s[1]}")
    c.drawString(50, 660, f"Roll Number: {s[2]}")
    c.drawString(50, 640, f"Course: {s[4]}")
    c.drawString(50, 620, f"CGPA: {s[5]}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 580, "Marks:")

    y = 560
    total_obt = 0
    total_max = 0

    c.setFont("Helvetica", 12)

    for sub, obt, maxm in marks:
        c.drawString(50, y, f"{sub}: {obt}/{maxm}")
        y -= 20
        total_obt += obt
        total_max += maxm

    if total_max > 0:
        percent = round((total_obt / total_max) * 100, 2)
        if percent >= 90:
            grade = "A+"
        elif percent >= 75:
            grade = "A"
        elif percent >= 60:
            grade = "B"
        elif percent >= 45:
            grade = "C"
        else:
            grade = "D"
    else:
        percent = 0
        grade = "N/A"

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, "Summary:")

    c.setFont("Helvetica", 12)
    c.drawString(50, y - 40, f"Total Marks: {total_obt}/{total_max}")
    c.drawString(50, y - 60, f"Percentage: {percent}%")
    c.drawString(50, y - 80, f"Grade: {grade}")

    c.showPage()
    c.save()

    return send_file(pdf_path, as_attachment=True)


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)