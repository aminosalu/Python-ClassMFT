# تمرین ۵ (نسخه peewee): وب‌اپ Flask
from flask import Flask, render_template, request, redirect, flash
from peewee import IntegrityError
from models import (db, create_tables, Department, Employee, check_in, check_out,
                    attendance_report, who_is_inside)

app = Flask(__name__)
app.secret_key = "dev-secret"
create_tables()


@app.route("/")
def index():
    inside = [{"first_name": a.employee.first_name, "last_name": a.employee.last_name,
               "check_in": a.check_in.strftime("%Y-%m-%d %H:%M:%S")} for a in who_is_inside()]
    return render_template("index.html", inside=inside)


@app.route("/checkin", methods=["POST"])
def do_checkin():
    flash(check_in(request.form["code"], request.form.get("note", "")))
    return redirect("/")


@app.route("/checkout", methods=["POST"])
def do_checkout():
    flash(check_out(request.form["code"]))
    return redirect("/")


@app.route("/employees")
def employees():
    rows = [{"personnel_code": e.personnel_code, "first_name": e.first_name,
             "last_name": e.last_name, "department": e.department.name}
            for e in Employee.select(Employee, Department).join(Department)]
    return render_template("employees.html", employees=rows, departments=Department.select())


@app.route("/departments/add", methods=["POST"])
def add_department():
    try:
        Department.create(name=request.form["name"], location=request.form.get("location", ""))
        flash("department added")
    except IntegrityError:
        flash("department already exists")
    return redirect("/employees")


@app.route("/employees/add", methods=["POST"])
def add_employee():
    try:
        Employee.create(personnel_code=request.form["code"], first_name=request.form["first"],
                        last_name=request.form["last"], department=int(request.form["department_id"]))
        flash("employee added")
    except (IntegrityError, ValueError):
        flash("could not add employee (duplicate code or no department?)")
    return redirect("/employees")


@app.route("/report")
def report():
    code = request.args.get("code", "")
    rows = None
    if code:
        if Employee.get_or_none(Employee.personnel_code == code) is None:
            flash("employee not found")
        else:
            rows = [{"check_in": i.strftime("%Y-%m-%d %H:%M:%S"),
                     "check_out": o.strftime("%Y-%m-%d %H:%M:%S") if o else None,
                     "hours": h} for i, o, h in attendance_report(code)]
    return render_template("report.html", code=code, rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
