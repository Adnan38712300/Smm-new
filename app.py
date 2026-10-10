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
TOPUP_BONUS = 5000
TOPUP_BONUS_AMOUNT = 200
CANCEL_WINDOW_MIN = 5
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
_memory_cache = {"data": None, "sha": None}

def _gh_headers():
    return {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "AdnanSMM"}

def gh_load():
    if not GH_TOKEN: return None
    try:
        req = urllib.request.Request(GH_API, headers=_gh_headers())
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.loads(r.read())
            _memory_cache["sha"] = j["sha"]
            return json.loads(base64.b64decode(j["content"]).decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404: _memory_cache["sha"] = None
        return None
    except: return None

def gh_save(data):
    if not GH_TOKEN: return False
    try:
        b64 = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
        if not _memory_cache["sha"]: gh_load()
        body = {"message": "Update data.json", "content": b64, "branch": "main"}
        if _memory_cache["sha"]: body["sha"] = _memory_cache["sha"]
        req = urllib.request.Request(GH_API, data=json.dumps(body).encode(),
            headers={**_gh_headers(), "Content-Type": "application/json"}, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as r:
            _memory_cache["sha"] = json.loads(r.read())["content"]["sha"]
        return True
    except: return False

def init_data():
    return {"users": {}, "orders": [], "payments": [], "announcements": [], "tickets": [],
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
            {"id":27,"cat":"Website","name":"Make Your Own Website","price":5000,"min_qty":1,"max_qty":2999},
            {"id":28,"cat":"TikTok","name":"TikTok Video Save","price":8,"min_qty":50,"max_qty":10000},
            {"id":29,"cat":"TikTok","name":"TikTok Video Shares","price":59,"min_qty":50,"max_qty":10000},
            {"id":30,"cat":"TikTok","name":"TikTok Live Stream Views","price":352,"min_qty":50,"max_qty":10000},
            {"id":31,"cat":"YouTube","name":"YouTube Shares (USA)","price":682,"min_qty":50,"max_qty":10000},
            {"id":32,"cat":"YouTube","name":"YouTube Shares (UK)","price":682,"min_qty":50,"max_qty":10000},
            {"id":33,"cat":"YouTube","name":"YouTube Shares (Indonesia)","price":682,"min_qty":50,"max_qty":10000},
            {"id":34,"cat":"YouTube","name":"YouTube Shares (Japan)","price":682,"min_qty":50,"max_qty":10000},
            {"id":35,"cat":"YouTube","name":"YouTube Views from Afghanistan","price":1452,"min_qty":50,"max_qty":10000},
            {"id":36,"cat":"YouTube","name":"YouTube Views from France","price":1452,"min_qty":50,"max_qty":10000},
            {"id":37,"cat":"YouTube","name":"YouTube Short Video Views [For Monetization]","price":2359,"min_qty":50,"max_qty":10000},
            {"id":38,"cat":"YouTube","name":"YouTube Likes (Refill 30D)","price":130,"min_qty":50,"max_qty":10000},
            {"id":39,"cat":"YouTube","name":"YouTube Comments (Custom)","price":999,"min_qty":50,"max_qty":10000},
            {"id":40,"cat":"Instagram","name":"Instagram Likes + Views + Repost","price":19,"min_qty":50,"max_qty":10000},
            {"id":41,"cat":"Instagram","name":"Instagram Channel Members","price":599,"min_qty":50,"max_qty":10000},
            {"id":42,"cat":"Instagram","name":"Instagram Likes (Female Users)","price":714,"min_qty":50,"max_qty":10000},
        ]}

def load_data():
    gh = gh_load()
    if gh:
        for k in ["payments","orders","users","services","announcements","tickets"]:
            if k not in gh: gh[k] = [] if k != "users" else {}
        _memory_cache["data"] = gh
        return gh
    if _memory_cache["data"]: return _memory_cache["data"]
    try:
        with open(DATA_FILE) as f: d = json.load(f)
        for k in ["payments","orders","users","services","announcements","tickets"]:
            if k not in d: d[k] = [] if k != "users" else {}
        _memory_cache["data"] = d
        return d
    except:
        d = init_data(); _memory_cache["data"] = d; return d

def save_data(d):
    _memory_cache["data"] = d
    # Retry 3 times on failure
    for i in range(3):
        if gh_save(d):
            break
        # Refresh SHA and retry
        _memory_cache["sha"] = None
        import time; time.sleep(0.5)

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
    active = len([o for o in user_orders if o.get("status") in ["Waiting","Processing","Pending"]])
    return {"total_spent": total_spent, "total_orders": 1247 + len(d["orders"]),
            "balance": balance, "status": status, "active_orders": active,
            "username": u.get("username", user.split("@")[0])}

def link_label(svc):
    n = svc["name"].lower()
    if "website" in n: return "WhatsApp Number"
    if any(k in n for k in ["like","view","comment","react","impression","vote","share","save"]): return "Video / Post Link"
    if any(k in n for k in ["follower","subscriber","member","channel"]): return "Account / Channel Link"
    return "Link"

def can_cancel(order):
    try:
        created = datetime.datetime.fromisoformat(order["created"])
        elapsed = (datetime.datetime.now() - created).total_seconds() / 60
        return elapsed <= CANCEL_WINDOW_MIN and order["status"] in ["Waiting","Pending"]
    except: return False

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
    return render_template("login.html", mode="login")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        pw = request.form.get("password","")
        uname = request.form.get("username","").strip() or email.split("@")[0]
        d = load_data()
        if not email or not pw:
            flash("Email aur password dono chahiye"); return redirect(url_for("signup"))
        if email in d["users"]:
            flash("Ye email already registered hai. Login karo."); return redirect(url_for("login"))
        d["users"][email] = {"pw": pw, "balance": 0, "username": uname, "created": str(datetime.datetime.now())}
        save_data(d)
        session.permanent = True
        session["user"] = email
        return redirect(url_for("home"))
    return render_template("login.html", mode="signup")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    d = load_data()
    stats = get_user_stats(d, session["user"])
    ann = d.get("announcements", [])
    latest = ann[-1] if ann else None
    return render_template("index.html", services=d["services"], stats=stats, announcement=latest)

@app.route("/profile", methods=["POST"])
@login_required
def profile():
    d = load_data()
    new_name = request.form.get("username","").strip()
    if new_name:
        d["users"][session["user"]]["username"] = new_name
        save_data(d); flash("Username update ho gaya ✔")
    return redirect(url_for("home"))

@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    d = load_data()
    old = request.form.get("old_password","")
    new = request.form.get("new_password","")
    if d["users"][session["user"]]["pw"] != old:
        flash("Purana password ghalat hai"); return redirect(url_for("home"))
    if len(new) < 4:
        flash("Naya password chhota hai"); return redirect(url_for("home"))
    d["users"][session["user"]]["pw"] = new
    save_data(d); flash("Password change ho gaya ✔")
    return redirect(url_for("home"))

@app.route("/add_funds")
@login_required
def add_funds():
    return render_template("add_funds.html", methods=PAYMENT_METHODS, bonus=TOPUP_BONUS, bonus_amt=TOPUP_BONUS_AMOUNT)

@app.route("/add_funds/next", methods=["POST"])
@login_required
def add_funds_next():
    method = request.form.get("method","")
    try:
        amount = float(request.form.get("amount",0) or 0)
    except:
        amount = 0
    if method not in PAYMENT_METHODS or amount < 10 or amount > 10000:
        flash("Sahi method aur amount (10-10000) daalo")
        return redirect(url_for("add_funds"))
    d = load_data()
    user_email = session["user"]
    # User missing ho to create karo
    if user_email not in d["users"]:
        d["users"][user_email] = {
            "pw": "",
            "balance": 0,
            "username": user_email.split("@")[0],
            "created": str(datetime.datetime.now())
        }
    user_obj = d["users"].get(user_email, {})
    bonus = TOPUP_BONUS_AMOUNT if amount >= TOPUP_BONUS else 0
    payid = "PAY" + datetime.datetime.now().strftime("%y%m%d") + str(secrets.token_hex(2)).upper()
    d["payments"].append({
        "id": payid, "user": user_email,
        "username": user_obj.get("username", user_email.split("@")[0]),
        "email": user_email, "method": method, "amount": amount,
        "bonus": bonus, "status": "Pending", "trx_id": "",
        "created": str(datetime.datetime.now())
    })
    save_data(d)
    return redirect(url_for("add_funds_pay", pid=payid))

@app.route("/add_funds/pay/<pid>")
@login_required
def add_funds_pay(pid):
    d = load_data()
    pay = next((p for p in d["payments"] if p["id"]==pid), None)
    if not pay: flash("Payment nahi mila"); return redirect(url_for("home"))
    method = PAYMENT_METHODS.get(pay["method"], {"name":"JazzCash","number":"—","owner":"—"})
    user_obj = d["users"].get(session["user"], {})
    username = user_obj.get("username", session["user"].split("@")[0])
    return render_template("add_funds_pay.html", pay=pay, method=method,
        whatsapp=WHATSAPP, username=username, useremail=session["user"])

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

@app.route("/payment_history")
@login_required
def payment_history():
    d = load_data()
    my_payments = [p for p in d["payments"] if p["user"] == session["user"]][::-1]
    stats = get_user_stats(d, session["user"])
    return render_template("payment_history.html", payments=my_payments, stats=stats)

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
    if not svc: return jsonify({"error":"Service nahi mili"}), 400
    charge = round((svc["price"]/1000) * qty, 2)
    user = session["user"]
    if user not in d["users"]:
        d["users"][user] = {"pw":"", "balance":0, "username": user.split("@")[0], "created": str(datetime.datetime.now())}
    balance = d["users"].get(user, {}).get("balance", 0)
    if balance < charge:
        return jsonify({"error":"insufficient","balance":balance,"needed":charge}), 400
    new_balance = round(balance - charge, 2)
    d["users"][user]["balance"] = new_balance
    oid = "ADN" + datetime.datetime.now().strftime("%y%m%d") + str(secrets.token_hex(2)).upper()
    d["orders"].append({
        "id": oid, "user": user,
        "username": d["users"][user].get("username", user.split("@")[0]),
        "service": svc["name"], "category": svc["cat"],
        "link": link, "qty": qty, "charge": charge,
        "status": "Waiting", "created": str(datetime.datetime.now())
    })
    save_data(d)
    return jsonify({"ok":True, "oid":oid, "new_balance":new_balance, "charge":charge})

@app.route("/cancel_order/<oid>")
@login_required
def cancel_order(oid):
    d = load_data()
    for o in d["orders"]:
        if o["id"] == oid and o["user"] == session["user"] and can_cancel(o):
            o["status"] = "Cancelled"
            d["users"][o["user"]]["balance"] = round(d["users"][o["user"]].get("balance",0) + o["charge"], 2)
            save_data(d)
            flash(f"Order cancel ho gaya. Rs {o['charge']} balance wapas ✔")
            return redirect(url_for("my_orders"))
    flash("Order cancel nahi ho sakta (time guzar gaya)")
    return redirect(url_for("my_orders"))

@app.route("/my_orders")
@login_required
def my_orders():
    d = load_data()
    orders = [o for o in d["orders"] if o["user"] == session["user"]][::-1]
    stats = get_user_stats(d, session["user"])
    return render_template("my_orders.html", orders=orders, stats=stats, can_cancel=can_cancel)

@app.route("/track")
@login_required
def track():
    oid = request.args.get("oid","").strip()
    order = None
    if oid:
        d = load_data()
        order = next((o for o in d["orders"] if o["id"]==oid), None)
    return render_template("track.html", order=order, oid=oid)

@app.route("/support")
@login_required
def support():
    d = load_data()
    my_tickets = [t for t in d["tickets"] if t["user"] == session["user"]][::-1]
    return render_template("support.html", tickets=my_tickets)

@app.route("/support/new", methods=["POST"])
@login_required
def support_new():
    d = load_data()
    subject = request.form.get("subject","").strip()
    message = request.form.get("message","").strip()
    if not subject or not message:
        flash("Subject aur message dono chahiye"); return redirect(url_for("support"))
    tid = "TKT" + str(secrets.token_hex(3)).upper()
    d["tickets"].append({
        "id": tid, "user": session["user"],
        "username": d["users"][session["user"]].get("username",""),
        "subject": subject, "message": message,
        "reply": "", "status": "Open",
        "created": str(datetime.datetime.now())
    })
    save_data(d); flash(f"Ticket {tid} submit ✔")
    return redirect(url_for("support"))

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
        announcements=d.get("announcements",[])[::-1],
        tickets=d.get("tickets",[])[::-1],
        edit_svc=edit_svc, tab=tab)

@app.route("/admin/order/<oid>/<status>")
@admin_required
def update_order(oid, status):
    d = load_data()
    for o in d["orders"]:
        if o["id"] == oid:
            old = o["status"]
            o["status"] = status
            if status == "Cancelled" and old != "Cancelled":
                d["users"][o["user"]]["balance"] = round(d["users"][o["user"]].get("balance",0) + o["charge"], 2)
    save_data(d)
    return redirect(url_for("admin_panel", tab="orders"))

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
                    total = p["amount"] + p.get("bonus", 0)
                    d["users"][email]["balance"] = round(cur + total, 2)
            if status == "Not Received" and old == "Received":
                email = p["user"]
                if email in d["users"]:
                    cur = d["users"][email].get("balance", 0)
                    total = p["amount"] + p.get("bonus", 0)
                    d["users"][email]["balance"] = round(max(0, cur - total), 2)
    save_data(d)
    return redirect(url_for("admin_panel", tab="payments"))

@app.route("/admin/add_service", methods=["POST"])
@admin_required
def add_service():
    d = load_data()
    new_id = max([s["id"] for s in d["services"]], default=0) + 1
    d["services"].append({"id": new_id, "cat": request.form.get("cat",""),
        "name": request.form.get("name",""), "price": float(request.form.get("price",0))})
    save_data(d)
    return redirect(url_for("admin_panel", tab="services"))

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
    save_data(d)
    return redirect(url_for("admin_panel", tab="services"))

@app.route("/admin/broadcast", methods=["POST"])
@admin_required
def broadcast():
    d = load_data()
    msg = request.form.get("message","").strip()
    if msg:
        d["announcements"].append({"msg": msg, "created": str(datetime.datetime.now())})
        save_data(d); flash("Broadcast bhej diya ✔")
    return redirect(url_for("admin_panel", tab="broadcast"))

@app.route("/admin/broadcast/delete/<int:idx>")
@admin_required
def broadcast_delete(idx):
    d = load_data()
    if 0 <= idx < len(d["announcements"]):
        d["announcements"].pop(idx)
        save_data(d)
    return redirect(url_for("admin_panel", tab="broadcast"))

@app.route("/admin/ticket/<tid>/reply", methods=["POST"])
@admin_required
def ticket_reply(tid):
    d = load_data()
    for t in d["tickets"]:
        if t["id"] == tid:
            t["reply"] = request.form.get("reply","").strip()
            t["status"] = "Closed"
    save_data(d); flash("Reply ✔")
    return redirect(url_for("admin_panel", tab="tickets"))

try: load_data()
except Exception as e: print("Init:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

@app.route("/admin/user/<path:email>/edit_balance", methods=["POST"])
@admin_required
def edit_balance(email):
    d = load_data()
    if email not in d["users"]:
        flash("User nahi mila")
        return redirect(url_for("admin_panel", tab="balance"))
    try:
        amount = float(request.form.get("amount", 0))
    except:
        flash("Ghalat amount")
        return redirect(url_for("admin_panel", tab="balance"))
    reason = request.form.get("reason", "Manual adjustment").strip() or "Manual adjustment"
    cur = d["users"][email].get("balance", 0)
    new_bal = round(cur + amount, 2)
    if new_bal < 0:
        new_bal = 0
    d["users"][email]["balance"] = new_bal
    if "balance_history" not in d["users"][email]:
        d["users"][email]["balance_history"] = []
    d["users"][email]["balance_history"].append({
        "amount": amount, "old": cur, "new": new_bal,
        "reason": reason, "date": str(datetime.datetime.now())
    })
    save_data(d)
    sign = "+" if amount >= 0 else ""
    flash(f"{email} ka balance {sign}Rs {amount} → Rs {new_bal} ✔")
    return redirect(url_for("admin_panel", tab="balance"))

@app.route("/admin/debug")
@admin_required
def debug():
    d = load_data()
    info = {
        "github_token_set": bool(GH_TOKEN),
        "github_token_len": len(GH_TOKEN),
        "github_user": GH_USER,
        "github_repo": GH_REPO,
        "cache_sha": _memory_cache.get("sha"),
        "orders_count": len(d.get("orders", [])),
        "payments_count": len(d.get("payments", [])),
        "users_count": len(d.get("users", {})),
        "last_payment": d["payments"][-1] if d.get("payments") else None,
    }
    return jsonify(info)
