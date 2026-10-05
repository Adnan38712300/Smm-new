import os, json, secrets, datetime, shutil
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

ADMIN_USER = "Adnan3871"
ADMIN_PASS = "Adnan123@"

def get_data_path():
    if os.path.exists("/tmp") and os.access("/tmp", os.W_OK):
        return "/tmp/data.json"
    return os.path.join(os.path.dirname(__file__), "data.json")

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
TMP_DATA = get_data_path()

PAYMENT_METHODS = {
    "jazzcash":  {"name": "JazzCash",  "number": "03037678443", "owner": "Abdul Majeed"},
    "easypaisa": {"name": "Easypaisa", "number": "Maintenance pr", "owner": "—"},
    "binance":   {"name": "Binance",   "number": "902574695",   "owner": "Binance ID"},
}

WHATSAPP = "03063871230"

def init_data():
    data = {
        "users": {},
        "orders": [],
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
    with open(TMP_DATA, "w") as f:
        json.dump(data, f, indent=2)
    return data

def load_data():
    if not os.path.exists(TMP_DATA):
        if TMP_DATA != DATA_FILE and os.path.exists(DATA_FILE):
            shutil.copy(DATA_FILE, TMP_DATA)
        else:
            return init_data()
    try:
        with open(TMP_DATA, "r") as f:
            return json.load(f)
    except:
        return init_data()

def save_data(d):
    with open(TMP_DATA, "w") as f:
        json.dump(d, f, indent=2)

def admin_required(f):
    @wraps(f)
    def wrap(*a, **k):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*a, **k)
    return wrap

def link_label(svc):
    n = svc["name"].lower()
    if any(k in n for k in ["like","view","comment","react","impression","vote"]):
        return "Video / Post Link"
    if any(k in n for k in ["follower","subscriber","member","channel"]):
        return "Account / Channel Link"
    if "website" in n:
        return "Apni Business ki Detail"
    return "Link"

# ===== PUBLIC =====
@app.route("/")
def home():
    d = load_data()
    return render_template("index.html", services=d["services"])

# ===== ORDER FLOW (NO LOGIN) =====
@app.route("/order/<int:sid>")
def order_page(sid):
    d = load_data()
    svc = next((s for s in d["services"] if s["id"]==sid), None)
    if not svc:
        flash("Service nahi mili")
        return redirect(url_for("home"))
    return render_template("order.html", svc=svc, methods=PAYMENT_METHODS, label=link_label(svc))

@app.route("/place_order", methods=["POST"])
def place_order():
    d = load_data()
    sid = int(request.form.get("service_id"))
    link = request.form.get("link","").strip()
    qty = int(request.form.get("quantity",100))
    method = request.form.get("method","jazzcash")
    svc = next((s for s in d["services"] if s["id"]==sid), None)
    if not svc:
        flash("Service nahi mili")
        return redirect(url_for("home"))
    charge = round((svc["price"]/1000) * qty, 2)
    oid = "ADN" + datetime.datetime.now().strftime("%y%m%d") + str(secrets.token_hex(2)).upper()
    d["orders"].append({
        "id": oid,
        "user": "guest",
        "service": svc["name"],
        "category": svc["cat"],
        "link": link,
        "qty": qty,
        "charge": charge,
        "method": method,
        "status": "Pending",
        "created": str(datetime.datetime.now())
    })
    save_data(d)
    return redirect(url_for("payment", oid=oid))

@app.route("/payment/<oid>")
def payment(oid):
    d = load_data()
    order = next((o for o in d["orders"] if o["id"]==oid), None)
    if not order:
        flash("Order nahi mila")
        return redirect(url_for("home"))
    method = PAYMENT_METHODS.get(order.get("method","jazzcash"), PAYMENT_METHODS["jazzcash"])
    return render_template("payment.html", order=order, method=method, whatsapp=WHATSAPP)

@app.route("/payment_done/<oid>")
def payment_done(oid):
    d = load_data()
    for o in d["orders"]:
        if o["id"]==oid:
            o["status"] = "Payment Submitted"
    save_data(d)
    return redirect(url_for("success", oid=oid))

@app.route("/success/<oid>")
def success(oid):
    return render_template("success.html", oid=oid)

@app.route("/track")
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
        u = request.form.get("username","")
        p = request.form.get("password","")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Ghalat credentials")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin_panel():
    d = load_data()
    orders = d["orders"][::-1]
    return render_template("admin.html", orders=orders, services=d["services"], users=d["users"], methods=PAYMENT_METHODS)

@app.route("/admin/order/<oid>/<status>")
@admin_required
def update_status(oid, status):
    d = load_data()
    for o in d["orders"]:
        if o["id"] == oid:
            o["status"] = status
    save_data(d)
    return redirect(url_for("admin_panel"))

@app.route("/admin/add_service", methods=["POST"])
@admin_required
def add_service():
    d = load_data()
    new_id = max([s["id"] for s in d["services"]], default=0) + 1
    d["services"].append({
        "id": new_id,
        "cat": request.form.get("cat",""),
        "name": request.form.get("name",""),
        "price": float(request.form.get("price",0))
    })
    save_data(d)
    return redirect(url_for("admin_panel"))

@app.route("/admin/del_service/<int:sid>")
@admin_required
def del_service(sid):
    d = load_data()
    d["services"] = [s for s in d["services"] if s["id"] != sid]
    save_data(d)
    return redirect(url_for("admin_panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

try:
    load_data()
except Exception as e:
    print("Init error:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
