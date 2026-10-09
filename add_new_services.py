import sqlite3, os, json

# GitHub se data load karo
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DATA_FILE = "/data/data/com.termux/files/home/smm-new/data.json"

# Nayi services ki list
NEW_SERVICES = [
    # TikTok
    ("TikTok", "TikTok Video Save", 8),
    ("TikTok", "TikTok Video Shares", 59),
    ("TikTok", "TikTok Live Stream Views", 352),

    # YouTube
    ("YouTube", "YouTube Shares (USA)", 682),
    ("YouTube", "YouTube Shares (UK)", 682),
    ("YouTube", "YouTube Shares (Indonesia)", 682),
    ("YouTube", "YouTube Shares (Japan)", 682),
    ("YouTube", "YouTube Views from Afghanistan", 1452),
    ("YouTube", "YouTube Views from France", 1452),
    ("YouTube", "YouTube Short Video Views [For Monetization]", 2359),
    ("YouTube", "YouTube Likes (Refill 30D)", 130),
    ("YouTube", "YouTube Comments (Custom)", 999),

    # Instagram
    ("Instagram", "Instagram Likes + Views + Repost", 19),
    ("Instagram", "Instagram Channel Members", 599),
    ("Instagram", "Instagram Likes (Female Users)", 714),
]

# Local data.json se load karo
with open(DATA_FILE) as f:
    d = json.load(f)

existing = d.get("services", [])
existing_ids = [s.get("id", 0) for s in existing]
next_id = max(existing_ids) + 1 if existing_ids else 1

added = 0
for cat, name, price in NEW_SERVICES:
    # Check duplicate
    if any(s.get("name") == name for s in existing):
        print(f"[SKIP] Already exists: {name}")
        continue
    existing.append({
        "id": next_id,
        "cat": cat,
        "name": name,
        "price": price,
        "min_qty": 50,
        "max_qty": 10000
    })
    print(f"[+] Added: {cat} | {name} | Rs {price}")
    next_id += 1
    added += 1

d["services"] = existing
with open(DATA_FILE, "w") as f:
    json.dump(d, f, indent=2)

print(f"\n[OK] {added} nayi services add ho gayi. Total ab: {len(existing)}")
