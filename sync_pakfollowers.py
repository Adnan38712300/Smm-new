import requests
from bs4 import BeautifulSoup
import re, json, os
from collections import Counter

PAKFOLLOWERS_URL = "https://pakfollowers.com/services"
COMMISSION = 0.25
DATA_FILE = "/data/data/com.termux/files/home/smm-new/data.json"

def guess_category(name):
    n = name.lower()
    if "tiktok" in n: return "TikTok"
    if "instagram" in n or "insta" in n: return "Instagram"
    if "youtube" in n or "yt " in n: return "YouTube"
    if "facebook" in n or "fb " in n: return "Facebook"
    if "twitter" in n: return "Twitter"
    if "telegram" in n: return "Telegram"
    if "whatsapp" in n: return "WhatsApp"
    if "website" in n or "seo" in n: return "Website"
    return "Other"

def clean_name(name):
    """Sirf main name rakho — description hatao"""
    # Flags/emojis hatao
    name = re.sub(r'[\U0001F000-\U0001FAFF]', '', name)
    name = re.sub(r'[\U0001F1E6-\U0001F1FF]', '', name)
    # Baaki text
    name = name.strip()
    
    # Pehla "|" ya "[" ke baad sab hatao (agar zyada lamba)
    if len(name) > 60:
        # Pehla | ya [ dhoondo
        for sep in [" |", " [", "|", "["]:
            idx = name.find(sep)
            if idx > 15 and idx < 60:
                name = name[:idx].strip()
                break
    
    # Baar baar spaces clean
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Trailing separators hatao
    name = name.rstrip('|- ,')
    
    return name

def scrape_services():
    r = requests.get(PAKFOLLOWERS_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text()
    
    blocks = text.split("View Details")
    services = []
    seen = set()
    
    for block in blocks:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if len(lines) < 5:
            continue
        
        id_idx = None
        for i, line in enumerate(lines):
            if re.fullmatch(r'\d{4,6}', line):
                id_idx = i
                break
        if id_idx is None:
            continue
        sid = lines[id_idx]
        
        price_idx = None
        for i in range(id_idx + 1, len(lines)):
            if lines[i].startswith("Rs "):
                price_idx = i
                break
        if price_idx is None:
            continue
        
        raw_name = " ".join(lines[id_idx + 1:price_idx]).strip()
        raw_name = re.sub(r'\s+', ' ', raw_name)
        name = clean_name(raw_name)
        
        if not name or name in seen:
            continue
        seen.add(name)
        
        pm = re.search(r'Rs\s*([\d.]+)', lines[price_idx])
        if not pm:
            continue
        try:
            price = float(pm.group(1))
        except:
            continue
        
        min_qty, max_qty = 50, 10000
        if price_idx + 1 < len(lines):
            try: min_qty = int(lines[price_idx + 1])
            except: pass
        if price_idx + 2 < len(lines):
            try: max_qty = int(lines[price_idx + 2])
            except: pass
        
        final_price = round(price * (1 + COMMISSION), 2)
        
        services.append({
            "name": name,
            "cat": guess_category(name),
            "price": final_price,
            "provider_id": sid,
            "min_qty": min_qty,
            "max_qty": max_qty,
            "per": 1000
        })
    
    return services

def sync():
    print("[*] Pakfollowers.com scrape...")
    scraped = scrape_services()
    print(f"[+] {len(scraped)} services mili")
    
    if not scraped:
        print("[!] Kuch nahi mila")
        return
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            d = json.load(f)
    else:
        d = {"users": {}, "orders": [], "payments": [], "announcements": [], "tickets": [], "services": []}
    
    old = len(d.get("services", []))
    d["services"] = []
    print(f"[+] Purani {old} services delete")
    
    for i, s in enumerate(scraped, 1):
        s["id"] = i
        d["services"].append(s)
    
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)
    
    print(f"[OK] {len(d['services'])} services add (25% commission)")
    
    counts = Counter(s["cat"] for s in d["services"])
    print("\n[*] Categories:")
    for cat, cnt in sorted(counts.items()):
        print(f"    {cat}: {cnt}")

if __name__ == "__main__":
    sync()
