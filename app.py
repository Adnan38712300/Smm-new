import os, json, secrets, datetime, shutil, base64, urllib.request, urllib.error
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = "AdnanSMM2026SecretKey_DoNotShare_9x7k2m4p1q8w"
app.permanent_session_lifetime = timedelta(days=365)

ADMIN_USER = "Adnan3871"
ADMIN_PASS = "Adnan123@"
SENIOR_THRESHOLD = 10000
WHATSAPP = "03063871230"

PAYMENT_METHODS = {
    "jazzcash":  {"name": "JazzCash",  "number": "03037678443", "owner": "Abdul Majeed"},
    "easypaisa": {"name": "Easypaisa", "number": "Maintenance pr", "owner": "—"},
    "binance":   {"name": "Binance",   "number": "902574695",   "owner": "Binance ID"},
}

GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_USER = os.environ.get("GITHUB_USER", "Adnan38712300")
GH_REPO = os.environ.get("GITHUB_REPO", "smm-new")
GH_FILE = "data.json"
GH_API = f"https://api.github.com/repos/{GH_USER}/{GH_REPO}/contents/{GH_FILE}"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
TMP_DATA = "/tmp/data.json"

_memory_cache = {"data": None, "sha": None}

def _gh_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AdnanSMM"
    }

def gh_load():
    if not GH_TOKEN:
        return None
    try:
        req = urllib.request.Request(GH_API, headers=_gh_headers())
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.loads(r.read())
            content = base64.b64decode(j["content"]).decode("utf-8")
            _memory_cache["sha"] = j["sha"]
            return json.loads(content)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            _memory_cache["sha"] = None
            return None
        return None
    except Exception:
        return None

def gh_save(data):
    if not GH_TOKEN:
        return False
    try:
        content = json.dumps(data, indent=2)
        b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        if not _memory_cache["sha"]:
            gh_load()
        body = {
            "message": "Update data.json",
            "content": b64,
            "branch": "main"
        }
        if _memory_cache["sha"]:
            body["sha"] = _memory_cache["sha"]
        req = urllib.request.Request(
            GH_API,
            data=json.dumps(body).encode("utf-8"),
            headers={**_gh_headers(), "Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.loads(r.read())
            _memory_cache["sha"] = j["content"]["sha"]
        return True
    except Exception as e:
        print("GH save error:", e)
        return False

def init_data():
    data = {
        "users": {}, "orders": [], "payments": [],
        "services": [
            {"id":1,"cat":"TikTok","name":"TikTok Likes Pharming System","price":495},
            {"id":2,"cat":"TikTok","name":"TikTok Pakistani Likes","price":750},
            {"id":3,"cat":"TikTok","name":"TikTok Video For You","price":250},
            {"id":4,"cat":"TikTok","name":"TikTok Mix Followers","price":4600},
            {"id":5,"cat":"TikTok","name":"TikTok Pakistani Followers","price":2500},
            {"id":6,"cat":"TikTok","name":"TikTok Followers Dropping Possible","price":600},
            {"id":7,"cat":"TikTok","name":"TikTok Comments Random","price":1100},
            {"id":8,"cat":"Instagram","name":"Instagram Followers","price":1000},
            {"id":9,"cat":"Instagram","name":"Instagram Likes","price":50},
            {"id":10,"cat":"Instagram","name":"Instagram Views","price":10},
            {"id":11,"cat":"YouTube","name":"YouTube Subscribers Original Users","price":15000},
            {"id":12,"cat":"YouTube","name":"YouTube Views","price":180},
            {"id":13,"cat":"YouTube","name":"YouTube Likes","price":350},
            {"id":14,"cat":"WhatsApp","name":"WhatsApp Pool Vote","price":450},
            {"id":15,"cat":"WhatsApp","name":"WhatsApp Channel Members","price":150},
            {"id":16,"cat":"WhatsApp","name":"WhatsApp Post React","price":350},
            {"id":17,"cat":"Facebook","name":"Facebook Followers (Dropping Possible)","price":55},
            {"id":18,"cat":"Facebook","name":"Facebook Post Reaction","price":50},
            {"id":19,"cat":"Facebook","name":"Facebook Views","price":23},
            {"id":20,"cat":"Facebook","name":"Facebook Comments","price":1140},
            {"id":21,"cat":"Twitter","name":"Twitter Followers","price":1050},
            {"id":22,"cat":"Twitter","name":"Twitter Likes","price":502},
            {"id":23,"cat":"Twitter","name":"Twitter Views + Impression","price":10},
            {"id":24,"cat":"Telegram","name":"Telegram Members","price":3200},
            {"id":25,"cat":"Telegram","name":"Telegram Members (Dropping Possible)","price":290},
            {"id":26,"cat":"Telegram","name":"Telegram React","price":10},
            {"id":27,"cat":"Website","name":"Make Your Own Website","price":5000},
        ]
    }
    with open(TMP_DATA, "w") as f: json.dump(data, f, indent=2)
    return data

def load_data():
    # Try GitHub first
    gh = gh_load()
    if gh:
        if "payments" not in gh: gh["payments"] = []
        if "orders" not in gh: gh["orders"] = []
        if "users" not in gh: gh["users"] = {}
        if "services" not in gh: gh["services"] = []
        _memory_cache["data"] = gh
        return gh
    # Fallback local
    if _memory_cache["data"]:
        return _memory_cache["data"]
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        _memory_cache["data"] = d
        return d
    except:
        d = init_data()
        _memory_cache["data"] = d
        return d

def save_data(d):
    _memory_cache["data"] = d
    gh_save(d)

def login_required(f):
    @wraps(f)
    def wrap(*a, **k):
        if not session.get("user"): return redirect(url_for("login"))
        return f(*a, **k)
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*a, **k):
        if not session.get("admin"): return redirect(url_for("admin_login"))
        return f(*a, **k)
    return wrap

def get_user_stats(d, user):
    u = d["users"].get(user, {})
    user_orders = [o for o in d["orders"] if o["user"] == user]
    total_spent = round(sum(o.get("charge",0) for o in user_orders if o.get("status") in ["Done","Complete"]), 2)
    balance = round(u.get("balance", 0), 2)
    status = "SENIOR" if total_spent > SENIOR_THRESHOLD else "JUNIOR"
    return {
        "total_spent": total_spent,
        "total_orders": 1247 + len(d["orders"]),
        "balance": balance,
        "status": status,
        "username": u.get("username", user.split("@")[0])
    }

def link_label(svc):
    n = svc["name"].lower()
    if any(k in n for k in ["like","view","comment","react","impression","vote"]): return "Video / Post Link"
    if any(k in n for k in ["follower","subscriber","member","channel"]): return "Account / Channel Link"
    if "website" in n: return "Apni Business ki Detail"
    return "Link"

# ===== AUTH =====
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        pw = request.form.get("password","")
        d = load_data()
        if email in d["users"] and d["users"][email]["pw"] == pw:
            session.permanent = True
            session["user"] = email
            return redirect(url_for("home"))
        flash("Ghalat email ya password")
    return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        pw = request.form.get("password","")
        d = load_data()
        if not email or not pw:
            flash("Email aur password dono chahiye"); return redirect(url_for("signup"))
        if email in d["users"]:
            flash("Ye email already registered hai. Login karo."); return redirect(url_for("login"))
        d["users"][email] = {"pw": pw, "balance": 0, "username": email.split("@")[0], "created": str(datetime.datetime.now())}
        save_data(d)
        session.permanent = True
        session["user"] = email
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

# ===== HOME =====
@app.route("/")
@login_required
def home():
    d = load_data()
    stats = get_user_stats(d, session["user"])
    order_placed = request.args.get("order_placed")
    return render_template("index.html", services=d["services"], stats=stats, order_placed=order_placed, whatsapp=WHATSAPP)

@app.route("/profile", methods=["POST"])
@login_required
def profile():
    d = load_data()
    new_name = request.form.get("username","").strip()
    if new_name:
        d["users"][session["user"]]["username"] = new_name
        save_data(d)
        flash("Username update ho gaya ✔")
    return redirect(url_for("home"))

# ===== ADD FUNDS =====
@app.route("/add_funds")
@login_required
def add_funds():
    return render_template("add_funds.html", methods=PAYMENT_METHODS)

@app.route("/add_funds/next", methods=["POST"])
@login_required
def add_funds_next():
    method = request.form.get("method","")
    amount = float(request.form.get("amount",0))
    if method not in PAYMENT_METHODS or amount < 10 or amount > 10000:
        flash("Sahi method aur amount (10-10000) daalo"); return redirect(url_for("add_funds"))
    d = load_data()
    payid = "PAY" + datetime.datetime.now().strftime("%y%m%d") + str(secrets.token_hex(2)).upper()
    d["payments"].append({
        "id": payid, "user": session["user"],
        "username": d["users"][session["user"]].get("username",""),
        "email": session["user"], "method": method, "amount": amount,
        "status": "Pending", "created": str(datetime.datetime.now())
    })
    save_data(d)
    return redirect(url_for("add_funds_pay", pid=payid))

@app.route("/add_funds/pay/<pid>")
@login_required
def add_funds_pay(pid):
    d = load_data()
    pay = next((p for p in d["payments"] if p["id"]==pid), None)
    if not pay: flash("Payment nahi mila"); return redirect(url_for("home"))
    method = PAYMENT_METHODS[pay["method"]]
    user_obj = d["users"].get(session["user"], {})
    username = user_obj.get("username", session["user"].split("@")[0])
    return render_template("add_funds_pay.html", pay=pay, method=method, whatsapp=WHATSAPP, username=username, useremail=session["user"])

@app.route("/add_funds/submit_trx/<pid>", methods=["POST"])
@login_required
def add_funds_submit_trx(pid):
    d = load_data()
    for p in d["payments"]:
        if p["id"]==pid:
            p["trx_id"] = request.form.get("trx_id","").strip()
            p["username"] = request.form.get("username","").strip()
            p["email"] = request.form.get("email","").strip()
            p["status"] = "Paid"
    save_data(d)
    return jsonify({"ok": True})

@app.route("/add_funds/thankyou/<pid>")
@login_required
def add_funds_thankyou(pid):
    return render_template("thankyou.html", pid=pid)

@app.route("/add_funds/done/<pid>")
@login_required
def add_funds_done(pid):
    d = load_data()
    for p in d["payments"]:
        if p["id"]==pid: p["status"] = "Paid"
    save_data(d)
    return render_template("add_funds_wait.html", pid=pid)

# ===== ORDERS =====
@app.route("/order/<int:sid>")
@login_required
def order_page(sid):
    d = load_data()
    svc = next((s for s in d["services"] if s["id"]==sid), None)
    if not svc: flash("Service nahi mili"); return redirect(url_for("home"))
    return render_template("order.html", svc=svc, label=link_label(svc))

@app.route("/place_order", methods=["POST"])
@login_required
def place_order():
    d = load_data()
    sid = int(request.form.get("service_id"))
    link = request.form.get("link","").strip()
    qty = int(request.form.get("quantity",100))
    svc = next((s for s in d["services"] if s["id"]==sid), None)
    if not svc:
        return jsonify({"error":"Service nahi mili"}), 400
    charge = round((svc["price"]/1000) * qty, 2)
    user = session["user"]
    balance = d["users"].get(user, {}).get("balance", 0)
    if balance < charge:
        return jsonify({"error":"insufficient","balance":balance,"needed":charge}), 400
    d["users"][user]["balance"] = round(balance - charge, 2)
    oid = "ADN" + datetime.datetime.now().strftime("%y%m%d") + str(secrets.token_hex(2)).upper()
    d["orders"].append({
        "id": oid, "user": user,
        "username": d["users"][user].get("username", user.split("@")[0]),
        "service": svc["name"], "category": svc["cat"],
        "link": link, "qty": qty, "charge": charge,
        "status": "Waiting", "created": str(datetime.datetime.now())
    })
    save_data(d)
    return jsonify({"ok":True, "oid":oid, "balance": d["users"][user]["balance"]})

@app.route("/my_orders")
@login_required
def my_orders():
    d = load_data()
    orders = [o for o in d["orders"] if o["user"] == session["user"]][::-1]
    stats = get_user_stats(d, session["user"])
    return render_template("my_orders.html", orders=orders, stats=stats)

@app.route("/track")
@login_required
def track():
    oid = request.args.get("oid","").strip()
    order = None
    if oid:
        d = load_data()
        order = next((o for o in d["orders"] if o["id"]==oid), None)
    return render_template("track.html", order=order, oid=oid)

# ===== ADMIN =====
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username",""); p = request.form.get("password","")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin"] = True; return redirect(url_for("admin_panel"))
        flash("Ghalat credentials")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin_panel():
    d = load_data()
    tab = request.args.get("tab","orders")
    edit_id = request.args.get("edit", type=int)
    edit_svc = None
    if edit_id:
        edit_svc = next((s for s in d["services"] if s["id"]==edit_id), None)
    return render_template("admin.html",
        orders=d["orders"][::-1], services=d["services"],
        payments=d["payments"][::-1], users=d["users"],
        edit_svc=edit_svc, tab=tab)

@app.route("/admin/order/<oid>/<status>")
@admin_required
def update_order(oid, status):
    d = load_data()
    for o in d["orders"]:
        if o["id"] == oid: o["status"] = status
    save_data(d); return redirect(url_for("admin_panel", tab="orders"))

@app.route("/admin/payment/<pid>/<status>")
@admin_required
def update_payment(pid, status):
    d = load_data()
    for p in d["payments"]:
        if p["id"] == pid:
            old = p["status"]
            p["status"] = status
            if status == "Received" and old != "Received":
                email = p["user"]
                if email in d["users"]:
                    cur = d["users"][email].get("balance", 0)
                    d["users"][email]["balance"] = round(cur + p["amount"], 2)
    save_data(d); return redirect(url_for("admin_panel", tab="payments"))

@app.route("/admin/add_service", methods=["POST"])
@admin_required
def add_service():
    d = load_data()
    new_id = max([s["id"] for s in d["services"]], default=0) + 1
    d["services"].append({"id": new_id, "cat": request.form.get("cat",""),
        "name": request.form.get("name",""), "price": float(request.form.get("price",0))})
    save_data(d); return redirect(url_for("admin_panel", tab="services"))

@app.route("/admin/edit_service/<int:sid>", methods=["POST"])
@admin_required
def edit_service(sid):
    d = load_data()
    for s in d["services"]:
        if s["id"] == sid:
            s["cat"] = request.form.get("cat", s["cat"])
            s["name"] = request.form.get("name", s["name"])
            s["price"] = float(request.form.get("price", s["price"]))
    save_data(d); flash("Service update ✔")
    return redirect(url_for("admin_panel", tab="services"))

@app.route("/admin/del_service/<int:sid>")
@admin_required
def del_service(sid):
    d = load_data()
    d["services"] = [s for s in d["services"] if s["id"] != sid]
    save_data(d); return redirect(url_for("admin_panel", tab="services"))

try: load_data()
except Exception as e: print("Init error:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
