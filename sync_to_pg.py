import os, re, requests
from bs4 import BeautifulSoup
import pg8000.dbapi as pg
import urllib.parse as urlparse

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("[!] DATABASE_URL set nahi"); exit(1)

# Direct connection (pooler hatao - fast)
DATABASE_URL = DATABASE_URL.replace("-pooler", "")

url = urlparse.urlparse(DATABASE_URL)
conn = pg.connect(user=url.username, password=url.password, host=url.hostname,
    port=url.port or 5432, database=url.path[1:] if url.path else "neondb",
    ssl_context=True, timeout=120)
c = conn.cursor()

def guess_cat(n):
    n = n.lower()
    if "tiktok" in n: return "TikTok"
    if "instagram" in n or "insta" in n: return "Instagram"
    if "youtube" in n or " yt " in n: return "YouTube"
    if "facebook" in n or " fb " in n: return "Facebook"
    if "twitter" in n: return "Twitter"
    if "telegram" in n or " tg " in n: return "Telegram"
    if "whatsapp" in n or " wa " in n or "pool vote" in n or "poll vote" in n: return "WhatsApp"
    if "twitch" in n: return "Twitch"
    if "spotify" in n: return "Spotify"
    if "linkedin" in n: return "LinkedIn"
    if "website" in n or "seo" in n or "traffic" in n: return "Website"
    return "Other"

def clean_name(name):
    name = re.sub(r'[\U0001F000-\U0001FAFF]', '', name).strip()
    if len(name) > 60:
        for sep in [" |", " [", "|", "["]:
            i = name.find(sep)
            if 15 < i < 60:
                name = name[:i].strip(); break
    return re.sub(r'\s+', ' ', name).rstrip('|- ,')

print("[*] Scraping...")
r = requests.get("https://pakfollowers.com/services",
                 headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
soup = BeautifulSoup(r.text, "html.parser")
text = soup.get_text()
blocks = text.split("View Details")
services = []
seen = set()

for block in blocks:
    lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
    if len(lines) < 5: continue
    id_idx = None
    for i, line in enumerate(lines):
        if re.fullmatch(r'\d{4,6}', line):
            id_idx = i; break
    if id_idx is None: continue
    price_idx = None
    for i in range(id_idx + 1, len(lines)):
        if lines[i].startswith("Rs "):
            price_idx = i; break
    if price_idx is None: continue
    raw = " ".join(lines[id_idx + 1:price_idx]).strip()
    name = clean_name(re.sub(r'\s+', ' ', raw))
    if not name or name in seen: continue
    seen.add(name)
    pm = re.search(r'Rs\s*([\d.]+)', lines[price_idx])
    if not pm: continue
    try: price = float(pm.group(1))
    except: continue
    min_q, max_q = 50, 10000
    if price_idx + 1 < len(lines):
        try: min_q = int(lines[price_idx + 1])
        except: pass
    if price_idx + 2 < len(lines):
        try: max_q = int(lines[price_idx + 2])
        except: pass
    final = round(price * 1.25, 2)
    services.append((guess_cat(name), name, final, min_q, max_q, lines[id_idx]))

print(f"[+] {len(services)} services")

print("[*] Purani delete + nayi single bulk insert...")

# Single multi-row insert
placeholders = ",".join(["(%s,%s,%s,%s,%s,%s,%s,%s)"] * len(services))
flat = []
for i, s in enumerate(services, 1):
    flat.extend([i, s[0], s[1], s[2], s[3], s[4], 1000, s[5]])

c.execute("DELETE FROM services")
c.execute(
    f"INSERT INTO services (id,cat,name,price,min_qty,max_qty,per,provider_id) VALUES {placeholders}",
    flat
)
conn.commit()

c.execute("SELECT COUNT(*) FROM services")
print(f"[OK] {c.fetchone()[0]} services insert ho gayi")
conn.close()
