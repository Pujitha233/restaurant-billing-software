# utils/db_utils.py
import sqlite3, os, csv, datetime

DB_PATH = os.path.join("db", "restaurant.db")
os.makedirs("db", exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        gst_percent REAL DEFAULT 5.0
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mode TEXT CHECK(mode IN ('Dine-In','Takeaway')) NOT NULL,
        payment_method TEXT CHECK(payment_method IN ('Cash','Card','UPI')) NOT NULL,
        subtotal REAL NOT NULL,
        gst REAL NOT NULL,
        discount REAL NOT NULL,
        total REAL NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        item_id INTEGER,
        item_name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        gst_percent REAL NOT NULL,
        line_total REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)
    conn.commit()

def load_menu_from_csv(csv_path):
    conn = get_conn()
    cur = conn.cursor()
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [(r["item_name"], r.get("category",""), float(r["price"]), float(r.get("gst_percent", 5)))
                for r in reader if r.get("item_name") and r.get("price")]
    cur.execute("DELETE FROM menu;")
    cur.executemany("INSERT INTO menu(item_name,category,price,gst_percent) VALUES(?,?,?,?)", rows)
    conn.commit()

def get_menu():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM menu ORDER BY category, item_name;").fetchall()
    return [dict(r) for r in rows]

def create_order(mode, payment_method, cart_items, subtotal, gst, discount, total):
    """cart_items: list of dicts {item_id, item_name, qty, unit_price, gst_percent, line_total}"""
    conn = get_conn()
    cur = conn.cursor()
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    cur.execute("""INSERT INTO orders(mode,payment_method,subtotal,gst,discount,total,created_at)
                   VALUES(?,?,?,?,?,?,?)""", (mode, payment_method, subtotal, gst, discount, total, ts))
    order_id = cur.lastrowid
    cur.executemany("""INSERT INTO order_items(order_id,item_id,item_name,qty,unit_price,gst_percent,line_total)
                       VALUES(?,?,?,?,?,?,?)""",
                    [(order_id, it.get("item_id"), it["item_name"], it["qty"], it["unit_price"], it["gst_percent"], it["line_total"])
                     for it in cart_items])
    conn.commit()
    return order_id, ts

def get_order(order_id):
    conn = get_conn()
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    items = conn.execute("SELECT * FROM order_items WHERE order_id=?",(order_id,)).fetchall()
    return dict(order) if order else None, [dict(i) for i in items]

def sales_summary(period="daily"):
    conn = get_conn()
    if period == "daily":
        fmt = "%Y-%m-%d"
    elif period == "weekly":
        fmt = "%Y-W%W"
    else:
        fmt = "%Y-%m"
    rows = conn.execute("SELECT * FROM orders").fetchall()
    # group in Python for simplicity
    from collections import defaultdict
    agg = defaultdict(lambda: {"orders":0,"subtotal":0.0,"gst":0.0,"discount":0.0,"total":0.0})
    import datetime as dt
    for r in rows:
        d = dt.datetime.fromisoformat(r["created_at"])
        key = d.strftime(fmt)
        a = agg[key]
        a["orders"] += 1
        a["subtotal"] += r["subtotal"]
        a["gst"] += r["gst"]
        a["discount"] += r["discount"]
        a["total"] += r["total"]
    return [{"period":k, **v} for k,v in sorted(agg.items())]

def most_sold_items(top_n=10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT item_name, SUM(qty) as qty
        FROM order_items GROUP BY item_name
        ORDER BY qty DESC LIMIT ?;
    """, (top_n,)).fetchall()
    return [dict(r) for r in rows]
