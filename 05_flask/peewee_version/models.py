# تمرین ۳: همون سیستم ورود و خروج، این بار با peewee ORM
from datetime import datetime
from peewee import (SqliteDatabase, Model, CharField, DateField, DateTimeField,
                    ForeignKeyField, IntegrityError)

db = SqliteDatabase("attendance_web.db", pragmas={"foreign_keys": 1})


class BaseModel(Model):
    class Meta:
        database = db


class Department(BaseModel):
    name = CharField(unique=True)
    location = CharField(default="")

    class Meta:
        table_name = "departments"


class Employee(BaseModel):
    personnel_code = CharField(unique=True)
    first_name = CharField()
    last_name = CharField()
    hire_date = DateField(default=datetime.now)
    # backref: از اداره می‌شه با department.employees به کارمندها رسید
    department = ForeignKeyField(Department, backref="employees")

    class Meta:
        table_name = "employees"


class Attendance(BaseModel):
    employee = ForeignKeyField(Employee, backref="attendances")
    check_in = DateTimeField(default=datetime.now)
    check_out = DateTimeField(null=True)
    note = CharField(default="")

    class Meta:
        table_name = "attendance"


def create_tables():
    db.connect(reuse_if_open=True)
    db.create_tables([Department, Employee, Attendance])


def check_in(code, note=""):
    emp = Employee.get_or_none(Employee.personnel_code == code)
    if emp is None:
        return "کارمندی با این کد پیدا نشد"
    open_row = Attendance.get_or_none(Attendance.employee == emp,
                                      Attendance.check_out.is_null())
    if open_row:
        return "این کارمند قبلاً وارد شده و هنوز خروج نزده"
    rec = Attendance.create(employee=emp, note=note)
    return f"ورود ثبت شد: {rec.check_in:%Y-%m-%d %H:%M:%S}"


def check_out(code):
    emp = Employee.get_or_none(Employee.personnel_code == code)
    if emp is None:
        return "کارمندی با این کد پیدا نشد"
    open_row = Attendance.get_or_none(Attendance.employee == emp,
                                      Attendance.check_out.is_null())
    if open_row is None:
        return "ورود بازی برای این کارمند وجود نداره"
    open_row.check_out = datetime.now()
    open_row.save()
    return f"خروج ثبت شد: {open_row.check_out:%Y-%m-%d %H:%M:%S}"


def attendance_report(code):
    """لیست (ورود، خروج، ساعت کارکرد)"""
    emp = Employee.get(Employee.personnel_code == code)
    result = []
    for a in emp.attendances.order_by(Attendance.check_in):
        hours = None
        if a.check_out:
            hours = round((a.check_out - a.check_in).total_seconds() / 3600, 2)
        result.append((a.check_in, a.check_out, hours))
    return result


def who_is_inside():
    return (Attendance.select(Attendance, Employee)
            .join(Employee)
            .where(Attendance.check_out.is_null()))


