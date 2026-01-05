import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

# ---------- DB CONFIG ----------
DB = {
    "host": "localhost",
    "user": "root",
    "password": "alexvsakha0123",
    "database": "Watchlist"
}

conn = pymysql.connect(**DB)
cur = conn.cursor()

# ---------- GUI ----------
root = tk.Tk()
root.title("AX Movies_editor")
root.geometry("1300x650")

# ---------- NOTEBOOK ----------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ==================================================
# TAB 1 : EDITOR (UNCHANGED CORE)
# ==================================================
editor_tab = tk.Frame(notebook)
notebook.add(editor_tab, text="Editor")

cols = ("id", "name", "year", "rating", "language", "industry")
tree = ttk.Treeview(editor_tab, columns=cols, show="headings")

for c in cols:
    tree.heading(c, text=c.upper())
    tree.column(c, width=160)

scroll = ttk.Scrollbar(editor_tab, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll.set)

tree.pack(side="left", fill="both", expand=True)
scroll.pack(side="left", fill="y")

# ---------- FORM ----------
form = tk.Frame(editor_tab, padx=10)
form.pack(side="right", fill="y")

def field(label):
    tk.Label(form, text=label).pack(anchor="w")
    e = tk.Entry(form, width=40)
    e.pack()
    return e

movie_id = field("Movie ID (readonly)")
movie_id.config(state="readonly")
name = field("Name")
year = field("Year")
rating = field("Rating")

tk.Label(form, text="Language").pack(anchor="w")
lang = ttk.Combobox(
    form,
    values=["Hindi","English","Tamil","Telugu","Kannada","Malayalam","Bengali","Marathi"],
    state="readonly"
)
lang.pack(fill="x")

tk.Label(form, text="Industry").pack(anchor="w")
industry = ttk.Combobox(
    form,
    values=["Bollywood","Hollywood","Kollywood","Tollywood","Mollywood","Sandalwood","Bihar","Bengal"],
    state="readonly"
)
industry.pack(fill="x")

# ---------- LOAD DATA ----------
def load():
    tree.delete(*tree.get_children())
    cur.execute("SELECT movie_id,name,year,rating,language,industry FROM Movies")
    for r in cur.fetchall():
        tree.insert("", "end", values=r)

# ---------- SELECT ----------
def select_row(event):
    if not tree.selection():
        return
    r = tree.item(tree.selection()[0])["values"]

    movie_id.config(state="normal")
    movie_id.delete(0,"end")
    movie_id.insert(0,r[0])
    movie_id.config(state="readonly")

    name.delete(0,"end")
    name.insert(0,r[1])

    year.delete(0,"end")
    year.insert(0,r[2] or "")

    rating.delete(0,"end")
    rating.insert(0,r[3])

    lang.set(r[4] or "")
    industry.set(r[5] or "")

tree.bind("<<TreeviewSelect>>", select_row)

# ---------- SAVE ----------
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
    messagebox.showinfo("Saved","Record updated successfully")

tk.Button(form, text="SAVE CHANGES", command=save, height=2).pack(fill="x", pady=10)

# ==================================================
# TAB 2 : FILTER (EXTENDED, NON-DESTRUCTIVE)
# ==================================================
filter_tab = tk.Frame(notebook)
notebook.add(filter_tab, text="Filter")

padx = 10

def f_label(txt):
    tk.Label(filter_tab, text=txt).pack(anchor="w", padx=padx, pady=3)

def f_entry():
    e = tk.Entry(filter_tab, width=40)
    e.pack(fill="x", padx=padx)
    return e

# -------- FILTER FIELDS --------
f_label("Movie ID")
f_id = f_entry()

f_label("Name (partial allowed)")
f_name = f_entry()

f_label("Year")
f_year = f_entry()

f_label("Rating (>=)")
f_rating = f_entry()

f_label("Language")
f_lang = ttk.Combobox(
    filter_tab,
    values=["Hindi","English","Tamil","Telugu","Kannada","Malayalam","Bengali","Marathi"],
    state="readonly"
)
f_lang.pack(fill="x", padx=padx)

f_label("Industry")
f_ind = ttk.Combobox(
    filter_tab,
    values=["Bollywood","Hollywood","Kollywood","Tollywood","Mollywood","Sandalwood","Bihar","Bengal"],
    state="readonly"
)
f_ind.pack(fill="x", padx=padx)

f_label("Actor (partial allowed)")
f_actor = f_entry()

f_label("Director (partial allowed)")
f_director = f_entry()

# -------- APPLY FILTER --------



def apply_filter():
    # if no filters are set, show all
    if not any([
        f_id.get(), f_name.get(), f_year.get(), f_rating.get(),
        f_lang.get(), f_ind.get(), f_actor.get(), f_director.get()
    ]):
        load()
        return

    tree.delete(*tree.get_children())

    q = """
    SELECT movie_id,name,year,rating,language,industry
    FROM Movies
    WHERE 1=1
    """
    params = []

    if f_id.get():
        q += " AND movie_id=%s"
        params.append(int(f_id.get()))

    if f_name.get():
        q += " AND name LIKE %s"
        params.append(f"%{f_name.get()}%")

    if f_year.get():
        q += " AND year=%s"
        params.append(int(f_year.get()))

    if f_rating.get():
        q += " AND rating >= %s"
        params.append(float(f_rating.get()))

    if f_lang.get():
        q += " AND language=%s"
        params.append(f_lang.get())

    if f_ind.get():
        q += " AND industry=%s"
        params.append(f_ind.get())

    # optional columns
    try:
        if f_actor.get():
            q += " AND actors LIKE %s"
            params.append(f"%{f_actor.get()}%")
        if f_director.get():
            q += " AND director LIKE %s"
            params.append(f"%{f_director.get()}%")
    except:
        pass

    cur.execute(q, params)
    for r in cur.fetchall():
        tree.insert("", "end", values=r)


# -------- RESET --------
def reset_filter():
    for w in filter_tab.winfo_children():
        if isinstance(w, tk.Entry):
            w.delete(0,"end")
        if isinstance(w, ttk.Combobox):
            w.set("")
    load()

tk.Button(filter_tab, text="APPLY FILTER", height=2, command=apply_filter).pack(pady=10)
tk.Button(filter_tab, text="RESET FILTER", command=reset_filter).pack()
# ---------- INIT ----------
load()
root.mainloop()
conn.close()
