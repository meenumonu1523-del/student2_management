
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student_management_secret"

# Database connection
def get_db_connection():
    conn = sqlite3.connect("college.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            course TEXT,
            email TEXT,
            marks REAL
        )
    """)

    conn.commit()
    conn.close()


# Dashboard
@app.route("/")
def index():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    average = conn.execute(
        "SELECT AVG(marks) FROM students"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        students=students,
        total=total,
        average=round(average or 0, 2)
    )


# Add student
@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]
        email = request.form["email"]
        marks = request.form["marks"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (name, age, course, email, marks)
            VALUES (?, ?, ?, ?, ?)
        """, (name, age, course, email, marks))

        conn.commit()
        conn.close()

        flash("Student added successfully!")

        return redirect(url_for("index"))

    return render_template("add_student.html")


# Search students
@app.route("/search")
def search():

    keyword = request.args.get("keyword", "")

    conn = get_db_connection()

    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
        OR course LIKE ?
        OR email LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    )).fetchall()

    conn.close()

    return render_template(
        "index.html",
        students=students,
        total=len(students),
        average=0,
        search_keyword=keyword
    )


# Edit student
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    if student is None:
        conn.close()
        flash("Student not found!")
        return redirect(url_for("index"))

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]
        email = request.form["email"]
        marks = request.form["marks"]

        conn.execute("""
            UPDATE students
            SET name=?, age=?, course=?, email=?, marks=?
            WHERE id=?
        """, (name, age, course, email, marks, id))

        conn.commit()
        conn.close()

        flash("Student updated successfully!")

        return redirect(url_for("index"))

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# Delete student
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!")

    return redirect(url_for("index"))


if __name__ == "__main__":

    create_table()

    app.run(debug=True)
