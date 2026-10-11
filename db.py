import os, json
import pg8000.dbapi as pg
import urllib.parse as urlparse

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_conn():
    url = urlparse.urlparse(DATABASE_URL)
    return pg.connect(
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port or 5432,
        database=url.path[1:] if url.path else "neondb",
        ssl_context=True
    )

def _dicts(cursor, rows, cols):
    return [dict(zip(cols, r)) for r in rows]

def init_tables():
    if not DATABASE_URL:
        print("[!] DATABASE_URL not set")
        return
    conn = get_conn()
    c = conn.cursor()
    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, pw TEXT, username TEXT,
            balance REAL DEFAULT 0, created TEXT)""",
        """CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY, cat TEXT, name TEXT, price REAL,
            min_qty INTEGER DEFAULT 50, max_qty INTEGER DEFAULT 10000,
            per INTEGER DEFAULT 1000, provider_id TEXT)""",
        """CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY, user_email TEXT, username TEXT,
            service TEXT, category TEXT, link TEXT, qty INTEGER,
            charge REAL, status TEXT DEFAULT 'Waiting', note TEXT,
            provider_order_id TEXT, created TEXT)""",
        """CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY, user_email TEXT, username TEXT,
            method TEXT, amount REAL, bonus REAL DEFAULT 0,
            trx_id TEXT, status TEXT DEFAULT 'Pending', created TEXT)""",
        """CREATE TABLE IF NOT EXISTS announcements (
            id SERIAL PRIMARY KEY, msg TEXT, created TEXT)""",
        """CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY, user_email TEXT, username TEXT,
            subject TEXT, message TEXT, reply TEXT,
            status TEXT DEFAULT 'Open', created TEXT)""",
    ]
    for t in tables:
        c.execute(t)
    conn.commit()
    conn.close()
    print("[OK] Tables ready")

def pg_load():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT email, pw, username, balance, created FROM users")
    cols = [d[0] for d in c.description]
    users = {r[0]: dict(zip(cols, r)) for r in c.fetchall()}

    c.execute("SELECT id, cat, name, price, min_qty, max_qty, per, provider_id FROM services ORDER BY cat, name")
    cols = [d[0] for d in c.description]
    services = _dicts(c, c.fetchall(), cols)

    c.execute("SELECT id, user_email, username, service, category, link, qty, charge, status, note, provider_order_id, created FROM orders ORDER BY created DESC")
    cols = [d[0] for d in c.description]
    orders = []
    for r in c.fetchall():
        o = dict(zip(cols, r)); o["user"] = o.pop("user_email"); orders.append(o)

    c.execute("SELECT id, user_email, username, method, amount, bonus, trx_id, status, created FROM payments ORDER BY created DESC")
    cols = [d[0] for d in c.description]
    payments = []
    for r in c.fetchall():
        p = dict(zip(cols, r)); p["user"] = p.pop("user_email"); payments.append(p)

    c.execute("SELECT id, msg, created FROM announcements ORDER BY id")
    cols = [d[0] for d in c.description]
    announcements = _dicts(c, c.fetchall(), cols)

    c.execute("SELECT id, user_email, username, subject, message, reply, status, created FROM tickets ORDER BY created DESC")
    cols = [d[0] for d in c.description]
    tickets = []
    for r in c.fetchall():
        t = dict(zip(cols, r)); t["user"] = t.pop("user_email"); tickets.append(t)

    conn.close()
    return {"users": users, "services": services, "orders": orders,
            "payments": payments, "announcements": announcements, "tickets": tickets}

def pg_save(d):
    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM users")
    for email, u in d.get("users", {}).items():
        c.execute("INSERT INTO users (email,pw,username,balance,created) VALUES (%s,%s,%s,%s,%s)",
            (email, u.get("pw",""), u.get("username",""), u.get("balance",0), u.get("created","")))

    c.execute("DELETE FROM services")
    for s in d.get("services", []):
        c.execute("INSERT INTO services (id,cat,name,price,min_qty,max_qty,per,provider_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (s["id"], s.get("cat",""), s.get("name",""), s.get("price",0),
             s.get("min_qty",50), s.get("max_qty",10000), s.get("per",1000), s.get("provider_id")))

    c.execute("DELETE FROM orders")
    for o in d.get("orders", []):
        c.execute("INSERT INTO orders (id,user_email,username,service,category,link,qty,charge,status,note,provider_order_id,created) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (o["id"], o.get("user",""), o.get("username",""), o.get("service",""),
             o.get("category",""), o.get("link",""), o.get("qty",0), o.get("charge",0),
             o.get("status","Waiting"), o.get("note",""), o.get("provider_order_id"), o.get("created","")))

    c.execute("DELETE FROM payments")
    for p in d.get("payments", []):
        c.execute("INSERT INTO payments (id,user_email,username,method,amount,bonus,trx_id,status,created) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (p["id"], p.get("user",""), p.get("username",""), p.get("method",""),
             p.get("amount",0), p.get("bonus",0), p.get("trx_id",""), p.get("status","Pending"), p.get("created","")))

    c.execute("DELETE FROM announcements")
    for a in d.get("announcements", []):
        c.execute("INSERT INTO announcements (msg,created) VALUES (%s,%s)", (a.get("msg",""), a.get("created","")))

    c.execute("DELETE FROM tickets")
    for t in d.get("tickets", []):
        c.execute("INSERT INTO tickets (id,user_email,username,subject,message,reply,status,created) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (t["id"], t.get("user",""), t.get("username",""), t.get("subject",""),
             t.get("message",""), t.get("reply",""), t.get("status","Open"), t.get("created","")))

    conn.commit()
    conn.close()
