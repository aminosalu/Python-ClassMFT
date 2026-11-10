# تمرین ۲: سیستم ورود و خروج کارکنان با SQLite خالص (ماژول sqlite3)
import sqlite3
from datetime import datetime

DB_NAME = "attendance.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")  # در SQLite به صورت پیش‌فرض خاموشه!
    conn.row_factory = sqlite3.Row            # دسترسی به ستون‌ها با اسم
    return conn


def create_tables():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS departments (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL UNIQUE,
            location TEXT
        );

        CREATE TABLE IF NOT EXISTS employees (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_code  TEXT NOT NULL UNIQUE,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            hire_date       TEXT,
            department_id   INTEGER NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            check_in    TEXT NOT NULL,
            check_out   TEXT,
            note        TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
    """)
    conn.commit()
    conn.close()


# ---------- بخش اداره‌ها ----------
def add_department(name, location=""):
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO departments (name, location) VALUES (?, ?)",
                           (name, location))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()   # حتی اگه خطا بیاد کانکشن بسته بشه (وگرنه دیتابیس قفل می‌شه)


# ---------- بخش کارمندها ----------
def add_employee(code, first, last, department_id, hire_date=None):
    hire_date = hire_date or datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO employees (personnel_code, first_name, last_name, hire_date, department_id) "
            "VALUES (?, ?, ?, ?, ?)", (code, first, last, hire_date, department_id))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_employee_by_code(code):
    conn = get_connection()
    row = conn.execute("SELECT * FROM employees WHERE personnel_code = ?", (code,)).fetchone()
    conn.close()
    return row


def list_employees():
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.personnel_code, e.first_name, e.last_name, d.name AS department
        FROM employees e JOIN departments d ON e.department_id = d.id
        ORDER BY e.last_name
    """).fetchall()
    conn.close()
    return rows


# ---------- ورود و خروج ----------
def check_in(code, note=""):
    emp = get_employee_by_code(code)
    if emp is None:
        return "کارمندی با این کد پیدا نشد"
    conn = get_connection()
    # اگه ورود باز (بدون خروج) داره، ورود دوباره مجاز نیست
    open_row = conn.execute(
        "SELECT id FROM attendance WHERE employee_id = ? AND check_out IS NULL",
        (emp["id"],)).fetchone()
    if open_row:
        conn.close()
        return "این کارمند قبلاً وارد شده و هنوز خروج نزده"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO attendance (employee_id, check_in, note) VALUES (?, ?, ?)",
                 (emp["id"], now, note))
    conn.commit()
    conn.close()
    return f"ورود ثبت شد: {now}"


def check_out(code):
    emp = get_employee_by_code(code)
    if emp is None:
        return "کارمندی با این کد پیدا نشد"
    conn = get_connection()
    open_row = conn.execute(
        "SELECT id FROM attendance WHERE employee_id = ? AND check_out IS NULL",
        (emp["id"],)).fetchone()
    if open_row is None:
        conn.close()
        return "ورود بازی برای این کارمند وجود نداره"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE attendance SET check_out = ? WHERE id = ?", (now, open_row["id"]))
    conn.commit()
    conn.close()
    return f"خروج ثبت شد: {now}"


def attendance_report(code):
    """گزارش ورود و خروج یک کارمند + مدت کارکرد به ساعت"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.check_in, a.check_out,
               ROUND((julianday(a.check_out) - julianday(a.check_in)) * 24, 2) AS hours
        FROM attendance a JOIN employees e ON a.employee_id = e.id
        WHERE e.personnel_code = ?
        ORDER BY a.check_in
    """, (code,)).fetchall()
    conn.close()
    return rows


def who_is_inside():
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.first_name, e.last_name, a.check_in
        FROM attendance a JOIN employees e ON a.employee_id = e.id
        WHERE a.check_out IS NULL
    """).fetchall()
    conn.close()
    return rows


# ---------- اجرای نمونه ----------
if __name__ == "__main__":
    import os
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)          # هر بار از اول تست می‌کنیم
    create_tables()

    d1 = add_department("IT", "Floor 1")
    d2 = add_department("HR", "Floor 2")
    add_employee("1001", "Ali", "Rezaei", d1)
    add_employee("1002", "Sara", "Ahmadi", d2)

    print(check_in("1001"))
    print(check_in("1001"))       # باید خطا بده
    print(check_in("1002", "دیر رسید"))
    print(check_out("1001"))
    print(check_out("1001"))      # باید خطا بده
    print(check_in("9999"))       # کد اشتباه

    print("\nلیست کارمندان:")
    for r in list_employees():
        print(" ", r["personnel_code"], r["first_name"], r["last_name"], "-", r["department"])

    print("\nهنوز داخل هستند:")
    for r in who_is_inside():
        print(" ", r["first_name"], r["last_name"], "از", r["check_in"])

    print("\nگزارش 1001:")
    for r in attendance_report("1001"):
        print(" ", r["check_in"], "->", r["check_out"], "|", r["hours"], "ساعت")

    # تست کلید خارجی: اداره‌ی ناموجود
    try:
        add_employee("1003", "Test", "Test", 99)
    except sqlite3.IntegrityError as e:
        print("\nخطای مورد انتظار:", e)
