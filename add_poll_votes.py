import os
import pg8000.dbapi as pg
import urllib.parse as urlparse

u = os.environ['DATABASE_URL'].replace('-pooler','')
url = urlparse.urlparse(u)
conn = pg.connect(user=url.username, password=url.password, host=url.hostname,
    port=url.port or 5432, database=url.path[1:] if url.path else "neondb", ssl_context=True)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM services WHERE name LIKE 'WhatsApp Poll Votes%'")
if c.fetchone()[0] == 0:
    c.execute("SELECT MAX(id) FROM services")
    max_id = c.fetchone()[0] or 0
    services = []
    for opt in ["A", "B", "C", "D", "E"]:
        max_id += 1
        services.append((max_id, "WhatsApp", f"WhatsApp Poll Votes ({opt})", 799.0, 50, 10000, 1000, "poll_" + opt.lower()))
    c.executemany(
        "INSERT INTO services (id,cat,name,price,min_qty,max_qty,per,provider_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        services
    )
    conn.commit()
    print(f"[+] 5 Poll Votes re-added")
else:
    print("[*] Poll Votes pehle se hain")

c.execute("UPDATE services SET price=109.99 WHERE name ILIKE '%whatsapp channel member%'")
conn.commit()
conn.close()
