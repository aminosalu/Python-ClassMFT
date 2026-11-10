# تمرین ۵ (نسخه SQLite خالص): وب‌اپ Flask
import sqlite3
from flask import Flask, render_template, request, redirect, flash
import db_sqlite as db

app = Flask(__name__)
app.secret_key = "dev-secret"   # برای flash لازمه
db.create_tables()


@app.route("/")
def index():
    return render_template("index.html", inside=db.who_is_inside())


@app.route("/checkin", methods=["POST"])
def do_checkin():
    flash(db.check_in(request.form["code"], request.form.get("note", "")))
    return redirect("/")


@app.route("/checkout", methods=["POST"])
def do_checkout():
    flash(db.check_out(request.form["code"]))
    return redirect("/")


@app.route("/employees")
def employees():
    conn = db.get_connection()
    deps = conn.execute("SELECT * FROM departments").fetchall()
    conn.close()
    return render_template("employees.html", employees=db.list_employees(), departments=deps)


@app.route("/departments/add", methods=["POST"])
def add_department():
    try:
        db.add_department(request.form["name"], request.form.get("location", ""))
        flash("department added")
    except sqlite3.IntegrityError:
        flash("department already exists")
    return redirect("/employees")


@app.route("/employees/add", methods=["POST"])
def add_employee():
    try:
        db.add_employee(request.form["code"], request.form["first"], request.form["last"],
                        int(request.form["department_id"]))
        flash("employee added")
    except (sqlite3.IntegrityError, ValueError):
        flash("could not add employee (duplicate code or no department?)")
    return redirect("/employees")


@app.route("/report")
def report():
    code = request.args.get("code", "")
    rows = db.attendance_report(code) if code else None
    return render_template("report.html", code=code, rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
