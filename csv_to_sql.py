import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import pymysql

# ================================
# ROOT
# ================================
root = tk.Tk()
root.title("AX CSV → SQL Importer")
root.geometry("1100x650")
root.configure(bg="#f4f6f9")

# ================================
# STYLE
# ================================
style = ttk.Style()
style.theme_use("clam")

style.configure("TNotebook", background="#f4f6f9")
style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=(14,8))

style.configure("TLabelframe", background="#ffffff", padding=10)
style.configure("TLabelframe.Label",
    font=("Segoe UI", 11, "bold"),
    foreground="#2c3e50"
)

style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
style.configure("TEntry", padding=6, font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=10)
style.configure("TCheckbutton", background="#ffffff")

# ================================
# VARIABLES
# ================================
csv_path = tk.StringVar(value="No file selected")
use_header = tk.BooleanVar(value=True)

detected_fields = []
detected_rows = 0

# ================================
# LAYOUT
# ================================
left = ttk.LabelFrame(root, text="CSV Detection")
left.pack(side="left", fill="both", expand=True, padx=12, pady=12)

right = ttk.LabelFrame(root, text="SQL Configuration & Insert")
right.pack(side="right", fill="both", expand=True, padx=12, pady=12)

# ================================
# LEFT PANEL (CSV)
# ================================
ttk.Label(left, textvariable=csv_path, wraplength=450).pack(anchor="w")

info = ttk.Label(left, text="No CSV loaded")
info.pack(anchor="w", pady=6)

ttk.Checkbutton(
    left,
    text="First row contains field names",
    variable=use_header
).pack(anchor="w", pady=6)

def upload_csv():
    global detected_fields, detected_rows

    path = filedialog.askopenfilename(
        filetypes=[("CSV Files","*.csv")]
    )
    if not path:
        return

    csv_path.set(path)

    with open(path, newline="", encoding="utf-8") as f:
        data = list(csv.reader(f))

    if not data:
        messagebox.showerror("Error", "CSV file is empty")
        return

    if use_header.get():
        detected_fields = data[0]
        detected_rows = len(data) - 1
    else:
        detected_fields = [f"field_{i+1}" for i in range(len(data[0]))]
        detected_rows = len(data)

    table_name.delete(0,"end")
    field_names.delete(0,"end")

    base = os.path.splitext(os.path.basename(path))[0]
    table_name.insert(0, base)
    field_names.insert(0, ",".join(detected_fields))

    info.config(
        text=f"Detected Fields: {len(detected_fields)}\nDetected Records: {detected_rows}"
    )

ttk.Button(left, text="Upload CSV", command=upload_csv, width=20).pack(pady=12)

# ================================
# RIGHT PANEL (SQL)
# ================================
def labeled_entry(parent, text):
    ttk.Label(parent, text=text).pack(anchor="w", pady=(8,0))
    e = ttk.Entry(parent)
    e.pack(fill="x")
    return e

db_host = labeled_entry(right, "MySQL Host")
db_user = labeled_entry(right, "MySQL User")
db_pass = labeled_entry(right, "MySQL Password")
db_name = labeled_entry(right, "Database Name")
table_name = labeled_entry(right, "Table Name")
field_names = labeled_entry(right, "Field Names (comma separated)")

db_host.insert(0, "localhost")
db_user.insert(0, "root")

def insert_csv_to_sql():
    if csv_path.get() == "No file selected":
        messagebox.showerror("Error", "No CSV selected")
        return

    fields = [f.strip() for f in field_names.get().split(",") if f.strip()]

    if not all([db_host.get(), db_user.get(), db_name.get(), table_name.get(), fields]):
        messagebox.showerror("Error", "Missing database, table or fields")
        return

    confirm = messagebox.askyesno(
        "Confirm Import",
        f"Database: {db_name.get()}\n"
        f"Table: {table_name.get()}\n"
        f"Fields: {len(fields)}\n"
        f"Records: {detected_rows}\n\nProceed?"
    )
    if not confirm:
        return

    try:
        conn = pymysql.connect(
            host=db_host.get(),
            user=db_user.get(),
            password=db_pass.get()
        )
        cur = conn.cursor()

        with open(csv_path.get(), newline="", encoding="utf-8") as f:
            data = list(csv.reader(f))

        start_idx = 1 if use_header.get() else 0
        rows = data[start_idx:]

        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name.get()}`")
        cur.execute(f"USE `{db_name.get()}`")

        cols = ", ".join([f"`{c}` TEXT NULL" for c in fields])
        cur.execute(f"CREATE TABLE IF NOT EXISTS `{table_name.get()}` ({cols})")

        placeholders = ",".join(["%s"] * len(fields))
        insert_q = f"INSERT INTO `{table_name.get()}` ({','.join(fields)}) VALUES ({placeholders})"

        for r in rows:
            values = [(v if v != "" else None) for v in r[:len(fields)]]
            while len(values) < len(fields):
                values.append(None)
            cur.execute(insert_q, values)

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Inserted {len(rows)} records into {db_name.get()}.{table_name.get()}"
        )

    except Exception as e:
        messagebox.showerror("SQL Error", str(e))

ttk.Button(
    right,
    text="Insert CSV into SQL",
    command=insert_csv_to_sql,
    width=28
).pack(pady=18)

# ================================
# START
# ================================
root.mainloop()
