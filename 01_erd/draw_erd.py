# رسم نمودار ERD سیستم مدیریت ورود و خروج کارکنان
# با matplotlib (ساده و بدون نیاز به نصب Graphviz)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# هر جدول: (عنوان، موقعیت x,y، لیست ستون‌ها)
tables = {
    "departments": (1, 8.5, ["PK  id", "name", "location"]),
    "employees": (7, 8.5, ["PK  id", "personnel_code (unique)", "first_name",
                         "last_name", "hire_date", "FK  department_id"]),
    "attendance": (7, 3.2, ["PK  id", "FK  employee_id", "check_in",
                          "check_out (nullable)", "note"]),
}
W, ROW = 4.2, 0.55

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 13)
ax.set_ylim(0, 10)
ax.axis("off")
ax.set_title("ERD - Employee Attendance System", fontsize=16, fontweight="bold")

boxes = {}
for name, (x, y, cols) in tables.items():
    h = ROW * (len(cols) + 1)
    # هدر جدول
    ax.add_patch(Rectangle((x, y), W, ROW, fc="#4a90d9", ec="black"))
    ax.text(x + W / 2, y + ROW / 2, name, ha="center", va="center",
            color="white", fontweight="bold", fontsize=12)
    # ستون‌ها
    for i, c in enumerate(cols):
        yy = y - ROW * (i + 1)
        ax.add_patch(Rectangle((x, yy), W, ROW, fc="#eaf2fb", ec="black"))
        ax.text(x + 0.2, yy + ROW / 2, c, va="center", fontsize=10,
                family="monospace")
    boxes[name] = (x, y - ROW * len(cols), W, h)

def arrow(p1, p2, l1, l2):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-", lw=1.8))
    if p1[0] == p2[0]:  # خط عمودی: عددها کنار خط
        ax.text(p1[0] + 0.25, p1[1] - 0.3, l1, fontsize=12, fontweight="bold")
        ax.text(p2[0] + 0.25, p2[1] + 0.2, l2, fontsize=12, fontweight="bold")
    else:  # خط افقی: عددها بالای خط
        ax.text(p1[0] + 0.2, p1[1] + 0.25, l1, fontsize=12, fontweight="bold", ha="center")
        ax.text(p2[0] - 0.2, p2[1] + 0.25, l2, fontsize=12, fontweight="bold", ha="center")

# departments (1) ---- (N) employees
arrow((1 + W, 8.0), (7, 8.0), "1", "N")
ax.text(6.1, 7.5, "has", ha="center", fontsize=10, style="italic")
# employees (1) ---- (N) attendance
arrow((9.1, 5.2), (9.1, 3.75), "1", "N")
ax.text(9.8, 4.4, "has records", fontsize=10, style="italic")

ax.text(1, 4.5, "Rules:\n- Each employee belongs to one department\n"
        "- Each employee has many attendance rows\n"
        "- check_out is NULL until the employee leaves",
        fontsize=10, va="top")
plt.savefig("erd.png", dpi=150, bbox_inches="tight")
print("erd.png saved")
