import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pymysql
import csv
import os
# ================================
# DB CONFIG
# ================================
DB = {
    "host": "localhost",
    "user": "root",
    "password": "alexvsakha0123",
    "database": "Watchlist"
}

conn = pymysql.connect(**DB)
cur = conn.cursor()

# ================================
# ROOT + STYLE (UI A)
# ================================
root = tk.Tk()

root.title("AX MySQL Manager")
root.geometry("1400x750")
root.configure(bg="#f4f6f9")

style = ttk.Style()
style.theme_use("clam")

# Notebook
style.configure("TNotebook", background="#f4f6f9", borderwidth=0)
style.configure("TNotebook.Tab",
    font=("Segoe UI", 11, "bold"),
    padding=(14,8)
)

# Frames
style.configure("TLabelframe", background="#ffffff", padding=10)
style.configure("TLabelframe.Label",
    font=("Segoe UI", 11, "bold"),
    foreground="#2c3e50"
)

# Labels
style.configure("TLabel",
    background="#ffffff",
    font=("Segoe UI", 10)
)

# Entries
style.configure("TEntry",
    padding=6,
    font=("Segoe UI", 10)
)

# Combobox
style.configure("TCombobox",
    padding=6,
    font=("Segoe UI", 10)
)

# Buttons
style.configure("TButton",
    font=("Segoe UI", 10, "bold"),
    padding=10
)

style.map("TButton",
    background=[("active","#3498db")],
    foreground=[("active","white")]
)

# ================================
# NOTEBOOK
# ================================
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# =====================================================
# TAB 1 : EDITOR
# =====================================================
editor_tab = ttk.Frame(notebook)
notebook.add(editor_tab, text="Editor")

tree_frame = ttk.Frame(editor_tab)
tree_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

form_frame = ttk.LabelFrame(editor_tab, text="Edit Record", padding=10)
form_frame.pack(side="right", fill="y", padx=10, pady=10)

cols = ("movie_id", "name", "year", "rating", "language", "industry")

tree = ttk.Treeview(tree_frame, columns=cols, show="headings")

for c in cols:
    tree.heading(c, text=c.upper())
    tree.column(c, width=140)

scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll.set)

tree.pack(side="left", fill="both", expand=True)
scroll.pack(side="left", fill="y")

def field(parent, label):
    ttk.Label(parent, text=label).pack(anchor="w", pady=(5, 0))
    e = ttk.Entry(parent, width=35)
    e.pack(fill="x")
    return e

movie_id = field(form_frame, "Movie ID")
movie_id.state(["readonly"])
name = field(form_frame, "Name")
year = field(form_frame, "Year")
rating = field(form_frame, "Rating")

ttk.Label(form_frame, text="Language").pack(anchor="w", pady=(5, 0))
lang = ttk.Combobox(form_frame,
    values=["Hindi","English","Tamil","Telugu","Kannada","Malayalam","Bengali","Marathi"],
    state="readonly"
)
lang.pack(fill="x")

ttk.Label(form_frame, text="Industry").pack(anchor="w", pady=(5, 0))
industry = ttk.Combobox(form_frame,
    values=["Bollywood","Hollywood","Kollywood","Tollywood","Mollywood","Sandalwood","Bihar","Bengal"],
    state="readonly"
)
industry.pack(fill="x")

def load():
    tree.delete(*tree.get_children())
    cur.execute("SELECT movie_id,name,year,rating,language,industry FROM Movies")
    for r in cur.fetchall():
        tree.insert("", "end", values=r)

def select_row(event):
    if not tree.selection():
        return
    r = tree.item(tree.selection()[0])["values"]

    movie_id.state(["!readonly"])
    movie_id.delete(0,"end")
    movie_id.insert(0,r[0])
    movie_id.state(["readonly"])

    name.delete(0,"end"); name.insert(0,r[1])
    year.delete(0,"end"); year.insert(0,r[2] or "")
    rating.delete(0,"end"); rating.insert(0,r[3])
    lang.set(r[4] or "")
    industry.set(r[5] or "")

tree.bind("<<TreeviewSelect>>", select_row)

def save():
    if not movie_id.get():
        return
    cur.execute("""
        UPDATE Movies
        SET name=%s, year=%s, rating=%s, language=%s, industry=%s
        WHERE movie_id=%s
    """, (
        name.get(),
        year.get() or None,
        rating.get(),
        lang.get() or None,
        industry.get() or None,
        movie_id.get()
    ))
    conn.commit()
    load()
    messagebox.showinfo("Saved", "Record updated successfully")

ttk.Button(form_frame, text="Save Changes", command=save).pack(fill="x", pady=10)

# =====================================================
# TAB 2 : FILTER
# =====================================================
filter_tab = ttk.Frame(notebook)
notebook.add(filter_tab, text="Filter")

filter_box = ttk.LabelFrame(filter_tab, text="Filter Options", padding=10)
filter_box.pack(fill="x", padx=20, pady=20)

def f_entry(lbl):
    ttk.Label(filter_box, text=lbl).pack(anchor="w")
    e = ttk.Entry(filter_box, width=40)
    e.pack(fill="x", pady=2)
    return e

f_id = f_entry("Movie ID")
f_name = f_entry("Name (partial)")
f_year = f_entry("Year")
f_rating = f_entry("Rating >= ")

ttk.Label(filter_box, text="Language").pack(anchor="w")
f_lang = ttk.Combobox(filter_box,
    values=["Hindi","English","Tamil","Telugu","Kannada","Malayalam","Bengali","Marathi"],
    state="readonly"
)
f_lang.pack(fill="x")

ttk.Label(filter_box, text="Industry").pack(anchor="w")
f_ind = ttk.Combobox(filter_box,
    values=["Bollywood","Hollywood","Kollywood","Tollywood","Mollywood","Sandalwood","Bihar","Bengal"],
    state="readonly"
)
f_ind.pack(fill="x")

def apply_filter():
    tree.delete(*tree.get_children())
    q = "SELECT movie_id,name,year,rating,language,industry FROM Movies WHERE 1=1"
    p = []

    if f_id.get(): q += " AND movie_id=%s"; p.append(f_id.get())
    if f_name.get(): q += " AND name LIKE %s"; p.append(f"%{f_name.get()}%")
    if f_year.get(): q += " AND year=%s"; p.append(f_year.get())
    if f_rating.get(): q += " AND rating >= %s"; p.append(f_rating.get())
    if f_lang.get(): q += " AND language=%s"; p.append(f_lang.get())
    if f_ind.get(): q += " AND industry=%s"; p.append(f_ind.get())

    cur.execute(q, p)
    for r in cur.fetchall():
        tree.insert("", "end", values=r)

ttk.Button(filter_box, text="Apply Filter", command=apply_filter).pack(pady=8)
ttk.Button(filter_box, text="Reset", command=load).pack()

# =====================================================
# TAB 3 : INSERT
# =====================================================
insert_tab = ttk.Frame(notebook)
notebook.add(insert_tab, text="Insert")

insert_box = ttk.LabelFrame(insert_tab, text="Insert New Record", padding=10)
insert_box.pack(padx=20, pady=20, fill="x")

i_name = field(insert_box, "Name")
i_year = field(insert_box, "Year")
i_rating = field(insert_box, "Rating")

ttk.Label(insert_box, text="Language").pack(anchor="w")
i_lang = ttk.Combobox(insert_box,
    values=["Hindi","English","Tamil","Telugu","Kannada","Malayalam","Bengali","Marathi"],
    state="readonly"
)
i_lang.pack(fill="x")

ttk.Label(insert_box, text="Industry").pack(anchor="w")
i_ind = ttk.Combobox(insert_box,
    values=["Bollywood","Hollywood","Kollywood","Tollywood","Mollywood","Sandalwood","Bihar","Bengal"],
    state="readonly"
)
i_ind.pack(fill="x")

def insert_record():
    
    cur.execute("""
        INSERT INTO Movies (name, year, rating, language, industry)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        i_name.get(),
        i_year.get() or None,
        i_rating.get(),
        i_lang.get() or None,
        i_ind.get() or None
    ))
    conn.commit()
    load()
    messagebox.showinfo("Inserted", "New record added")

ttk.Button(insert_box, text="Insert Record", command=insert_record).pack(pady=10)

# =====================================================
# TAB 4 : CSV → SQL
# =====================================================
csv_tab = ttk.Frame(notebook)
notebook.add(csv_tab, text="CSV → SQL")

left = ttk.LabelFrame(csv_tab, text="CSV Detection", padding=10)
left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

right = ttk.LabelFrame(csv_tab, text="Edit Before Insert", padding=10)
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

csv_path = tk.StringVar(value="No file selected")
use_header = tk.BooleanVar(value=True)
detected_rows = 0
detected_fields = []

# ---------- LEFT PANEL ----------
ttk.Label(left, textvariable=csv_path, wraplength=400).pack(anchor="w")

info = ttk.Label(left, text="No CSV loaded")
info.pack(anchor="w", pady=6)

ttk.Checkbutton(
    left,
    text="First row contains field names",
    variable=use_header
).pack(anchor="w", pady=5)

def upload_csv():
    global detected_rows, detected_fields

    path = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
    if not path:
        return

    csv_path.set(path)

    with open(path, newline="", encoding="utf-8") as f:
        data = list(csv.reader(f))

    if not data:
        messagebox.showerror("Error", "Empty CSV file")
        return

    if use_header.get():
        detected_fields = data[0]
        detected_rows = len(data) - 1
    else:
        detected_fields = [f"field_{i+1}" for i in range(len(data[0]))]
        detected_rows = len(data)

    db_name.delete(0,"end")
    table_name.delete(0,"end")

    base = os.path.splitext(os.path.basename(path))[0]
    
    table_name.insert(0, base)

    field_names.delete(0,"end")
    field_names.insert(0, ",".join(detected_fields))

    info.config(
        text=f"Detected Fields: {len(detected_fields)}\nDetected Records: {detected_rows}"
    )

ttk.Button(left, text="Upload CSV", command=upload_csv, width=20).pack(pady=10)

# ---------- RIGHT PANEL ----------
def labeled_entry(parent, text):
    ttk.Label(parent, text=text).pack(anchor="w", pady=(6,0))
    e = ttk.Entry(parent)
    e.pack(fill="x")
    return e

db_name = labeled_entry(right, "Database Name")
table_name = labeled_entry(right, "Table Name")
field_names = labeled_entry(right, "Field Names (comma separated)")

def insert_csv_to_sql():
    if not csv_path.get() or csv_path.get() == "No file selected":
        messagebox.showerror("Error", "No CSV selected")
        return

    db = db_name.get().strip()
    table = table_name.get().strip()
    fields = [f.strip() for f in field_names.get().split(",") if f.strip()]

    if not db or not table or not fields:
        messagebox.showerror("Error", "Database, table or fields missing")
        return

    confirm = messagebox.askyesno(
        "Confirm Insert",
        f"Database: {db}\nTable: {table}\nFields: {len(fields)}\nRecords: {detected_rows}\n\nProceed?"
    )
    if not confirm:
        return

    with open(csv_path.get(), newline="", encoding="utf-8") as f:
        data = list(csv.reader(f))

    start_idx = 1 if use_header.get() else 0
    rows = data[start_idx:]

    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`")
    cur.execute(f"USE `{db}`")

    cols = ", ".join([f"`{c}` TEXT NULL" for c in fields])
    cur.execute(f"CREATE TABLE IF NOT EXISTS `{table}` ({cols})")

    placeholders = ",".join(["%s"] * len(fields))
    insert_q = f"INSERT INTO `{table}` ({','.join(fields)}) VALUES ({placeholders})"

    for r in rows:
        values = [(v if v != "" else None) for v in r[:len(fields)]]
        while len(values) < len(fields):
            values.append(None)
        cur.execute(insert_q, values)

    conn.commit()

    messagebox.showinfo(
        "Success",
        f"Inserted {len(rows)} records into {db}.{table}"
    )

ttk.Button(
    right,
    text="Insert CSV into SQL",
    command=insert_csv_to_sql,
    width=25
).pack(pady=15)
# =====================================================
# TAB 6 : SQL → DELETE
# =====================================================
delete_tab = ttk.Frame(notebook)
notebook.add(delete_tab, text="Delete Records")

del_box = ttk.LabelFrame(delete_tab, text="Delete Records from Table", padding=10)
del_box.pack(padx=20, pady=20, fill="both", expand=True)

db_del = labeled_entry(del_box, "Database Name")
table_del = labeled_entry(del_box, "Table Name")
where_del = labeled_entry(del_box, "WHERE Clause (optional)")

del_tree_frame = ttk.Frame(del_box)
del_tree_frame.pack(fill="both", expand=True, pady=10)

del_tree = ttk.Treeview(del_tree_frame)
del_scroll = ttk.Scrollbar(del_tree_frame, orient="vertical", command=del_tree.yview)
del_tree.configure(yscrollcommand=del_scroll.set)
del_tree.pack(side="left", fill="both", expand=True)
del_scroll.pack(side="left", fill="y")

# Dictionary to store column names
del_columns = []

def load_delete_records():
    global del_columns
    db = db_del.get().strip()
    table = table_del.get().strip()
    if not db or not table:
        messagebox.showerror("Error", "Database and table required")
        return
    try:
        cur.execute(f"USE `{db}`")
        # Get columns
        cur.execute(f"DESCRIBE `{table}`")
        cols = [row[0] for row in cur.fetchall()]
        del_columns = cols

        # Clear previous Treeview
        del_tree.delete(*del_tree.get_children())
        del_tree.config(columns=cols, show="headings")
        for c in cols:
            del_tree.heading(c, text=c.upper())
            del_tree.column(c, width=120)

        # Fetch data
        q = f"SELECT * FROM `{table}`"
        where = where_del.get().strip()
        if where:
            q += f" WHERE {where}"
        cur.execute(q)
        rows = cur.fetchall()
        for r in rows:
            del_tree.insert("", "end", values=r)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_records():
    db = db_del.get().strip()
    table = table_del.get().strip()
    selected = del_tree.selection()
    if not db or not table:
        messagebox.showerror("Error", "Database and table required")
        return
    if not selected:
        messagebox.showerror("Error", "Select at least one record to delete")
        return

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} record(s)?")
    if not confirm:
        return

    try:
        cur.execute(f"USE `{db}`")
        pk_col = del_columns[0]  # Assumes first column is PK
        for s in selected:
            row = del_tree.item(s)["values"]
            cur.execute(f"DELETE FROM `{table}` WHERE `{pk_col}`=%s", (row[0],))
        conn.commit()
        load_delete_records()
        messagebox.showinfo("Deleted", f"{len(selected)} record(s) deleted successfully")
    except Exception as e:
        messagebox.showerror("Error", str(e))

ttk.Button(del_box, text="Load Records", command=load_delete_records).pack(pady=5)
ttk.Button(del_box, text="Delete Selected", command=delete_records).pack(pady=5)

# ================================
# INIT
# ================================
load()
root.mainloop()
conn.close()
