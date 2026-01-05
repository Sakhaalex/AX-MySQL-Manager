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
root.title("Movie Editor (Single Record)")
root.geometry("1200x600")

# ---------- TABLE ----------
cols = ("id", "name", "year", "rating", "language", "industry")
tree = ttk.Treeview(root, columns=cols, show="headings")

for c in cols:
    tree.heading(c, text=c.upper())
    tree.column(c, width=160)

scroll = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll.set)

tree.pack(side="left", fill="both", expand=True)
scroll.pack(side="left", fill="y")

# ---------- FORM ----------
form = tk.Frame(root, padx=10)
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
    messagebox.showinfo("Saved","Record updated")

tk.Button(form,text="SAVE CHANGES",command=save,height=2).pack(fill="x",pady=10)

# ---------- INIT ----------
load()
root.mainloop()
conn.close()
