"""
Smart Canteen Pre-Order System
Flask Backend  –  app.py  (SQLite version)
Run: python app.py
Open: http://127.0.0.1:5000
"""

import os
import sqlite3
import random
import string
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash, g)
from werkzeug.security import generate_password_hash, check_password_hash

# ─────────────────────── App Setup ────────────────────────────
app = Flask(__name__)
app.secret_key = "smart_canteen_secret_key_2024"

# ─────────────────────── DB Path ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "canteen.db")


# ─────────────────────── DB Connection ────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=30.0)
        g.db.row_factory = sqlite3.Row   # dict-like rows
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
        g.db.execute("PRAGMA busy_timeout = 30000")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ─────────────────────── Helpers ──────────────────────────────
def gen_order_id():
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"SC{datetime.now().strftime('%y%m')}{suffix}"


def calc_prep_time(total_qty: int) -> str:
    if total_qty <= 2:
        return "5 – 10 minutes"
    elif total_qty <= 4:
        return "10 – 15 minutes"
    else:
        return "15 – 20 minutes"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            flash("Admin login required.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────── DB Init ──────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    cur  = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            roll_number TEXT    NOT NULL UNIQUE,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS admin (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS food_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            description  TEXT,
            price        REAL    NOT NULL,
            category     TEXT    NOT NULL
                         CHECK(category IN ('Breakfast','Meals','Snacks','Drinks')),
            image_url    TEXT,
            is_available INTEGER DEFAULT 1,
            created_at   TEXT    DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id     TEXT    NOT NULL UNIQUE,
            user_id      INTEGER NOT NULL,
            total_amount REAL    NOT NULL,
            pickup_time  TEXT    NOT NULL,
            status       TEXT    DEFAULT 'Pending'
                         CHECK(status IN
                           ('Pending','Accepted','Preparing','Ready','Completed','Cancelled')),
            prep_time    TEXT,
            created_at   TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id     TEXT    NOT NULL,
            food_item_id INTEGER NOT NULL,
            quantity     INTEGER NOT NULL DEFAULT 1,
            unit_price   REAL    NOT NULL,
            FOREIGN KEY (order_id)     REFERENCES orders(order_id)   ON DELETE CASCADE,
            FOREIGN KEY (food_item_id) REFERENCES food_items(id)     ON DELETE CASCADE
        );
    """)

    # Default admin  (password: admin123)
    cur.execute("SELECT COUNT(*) FROM admin")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO admin (username, password) VALUES (?,?)",
            ("admin", generate_password_hash("admin123"))
        )

    # Seed food items
    cur.execute("SELECT COUNT(*) FROM food_items")
    if cur.fetchone()[0] == 0:
        items = [
            # Breakfast
            ("Masala Dosa",     "Crispy dosa filled with spiced potato masala, served with coconut chutney & sambar", 35.00,  "Breakfast", "dosa.jpg",        1),
            ("Idli Sambar",     "3 soft steamed idlis served with hot sambar and 2 chutneys",                          25.00,  "Breakfast", "idli.jpg",        1),
            ("Poha",            "Flattened rice cooked with onions, peas, peanuts and Indian spices",                  20.00,  "Breakfast", "poha.jpg",        1),
            ("Upma",            "Semolina porridge tempered with mustard, curry leaves and vegetables",                20.00,  "Breakfast", "upma.jpg",        1),
            # Meals
            ("Veg Thali",       "Full meal: rice, 2 rotis, dal, 2 sabzis, raita, pickle & dessert",                   80.00,  "Meals",     "thali.jpg",       1),
            ("Chicken Biryani", "Aromatic basmati rice cooked with tender chicken and whole spices",                  110.00, "Meals",     "biryani.jpg",     1),
            ("Paneer Rice",     "Basmati rice sauteed with paneer cubes and mixed vegetables",                         70.00,  "Meals",     "paneer_rice.jpg", 1),
            ("Chole Bhature",   "Spicy chickpea curry served with 2 fluffy fried bhature",                             60.00,  "Meals",     "chole.jpg",       1),
            # Snacks
            ("Samosa",          "2 crispy pastry pockets stuffed with spiced potatoes & peas",                         20.00,  "Snacks",    "samosa.jpg",      1),
            ("Vada Pav",        "Mumbai street-style spiced potato fritter in a soft bun",                             15.00,  "Snacks",    "vada_pav.jpg",    1),
            ("Bhel Puri",       "Puffed rice with veggies, chutneys & sev",                                            25.00,  "Snacks",    "bhel.jpg",        1),
            ("Bread Pakora",    "Bread slices in spiced gram-flour batter, deep fried",                                30.00,  "Snacks",    "pakora.jpg",      1),
            # Drinks
            ("Cold Coffee",     "Chilled blended coffee with milk and ice cream",                                       50.00,  "Drinks",    "coffee.jpg",      1),
            ("Mango Lassi",     "Thick sweet lassi blended with fresh mango pulp",                                     40.00,  "Drinks",    "lassi.jpg",       1),
            ("Masala Chai",     "Strong Indian spiced tea with ginger, cardamom and milk",                             15.00,  "Drinks",    "chai.jpg",        1),
            ("Fresh Lime Soda", "Freshly squeezed lime soda – sweet, salted or both",                                  25.00,  "Drinks",    "lime_soda.jpg",   1),
        ]
        cur.executemany(
            "INSERT INTO food_items (name,description,price,category,image_url,is_available) "
            "VALUES (?,?,?,?,?,?)",
            items
        )

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ─── Register ────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name        = request.form["name"].strip()
        roll_number = request.form["roll_number"].strip()
        email       = request.form["email"].strip().lower()
        password    = request.form["password"]
        confirm     = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (name,roll_number,email,password) VALUES (?,?,?,?)",
                (name, roll_number, email, hashed)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Roll number or email already registered.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# ─── Login ───────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("menu"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


# ─── Logout ──────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.pop("user_id",   None)
    session.pop("user_name", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ─── Menu ────────────────────────────────────────────────────
@app.route("/menu")
@login_required
def menu():
    conn  = get_db()
    rows  = conn.execute(
        "SELECT * FROM food_items WHERE is_available=1 ORDER BY category,name"
    ).fetchall()

    categories = {}
    for row in rows:
        cat = row["category"]
        categories.setdefault(cat, []).append(dict(row))

    return render_template("menu.html", categories=categories)


# ─── Cart ────────────────────────────────────────────────────
@app.route("/cart")
@login_required
def cart():
    return render_template("cart.html")


# ─── Place Order ─────────────────────────────────────────────
@app.route("/place-order", methods=["POST"])
@login_required
def place_order():
    data        = request.get_json() or {}
    cart_items  = data.get("items", [])
    pickup_time = data.get("pickup_time", "")

    if not cart_items or not pickup_time:
        return jsonify({"success": False, "message": "Cart or pickup time missing"}), 400

    total_qty = sum(int(i["quantity"]) for i in cart_items)
    prep_time = calc_prep_time(total_qty)
    order_id  = gen_order_id()

    conn         = get_db()
    total_amount = 0.0
    validated    = []

    for item in cart_items:
        row = conn.execute(
            "SELECT id,price FROM food_items WHERE id=? AND is_available=1",
            (item["food_item_id"],)
        ).fetchone()
        if not row:
            return jsonify({"success": False,
                            "message": f"Item {item['food_item_id']} not available"}), 400
        qty   = int(item["quantity"])
        price = float(row["price"])
        total_amount += price * qty
        validated.append((order_id, row["id"], qty, price))

    conn.execute(
        "INSERT INTO orders (order_id,user_id,total_amount,pickup_time,status,prep_time) "
        "VALUES (?,?,?,?,'Pending',?)",
        (order_id, session["user_id"], round(total_amount, 2), pickup_time, prep_time)
    )
    conn.executemany(
        "INSERT INTO order_items (order_id,food_item_id,quantity,unit_price) VALUES (?,?,?,?)",
        validated
    )
    conn.commit()

    return jsonify({
        "success":    True,
        "order_id":   order_id,
        "total":      round(total_amount, 2),
        "prep_time":  prep_time,
        "pickup_time": pickup_time
    })


# ─── Order Confirmation ──────────────────────────────────────
@app.route("/order-confirmation/<order_id>")
@login_required
def order_confirmation(order_id):
    conn = get_db()
    order = conn.execute(
        "SELECT o.*, u.name AS student_name "
        "FROM orders o JOIN users u ON o.user_id=u.id "
        "WHERE o.order_id=? AND o.user_id=?",
        (order_id, session["user_id"])
    ).fetchone()

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("orders"))

    items = conn.execute(
        "SELECT oi.quantity, oi.unit_price, f.name "
        "FROM order_items oi JOIN food_items f ON oi.food_item_id=f.id "
        "WHERE oi.order_id=?",
        (order_id,)
    ).fetchall()

    order = dict(order)
    items = [dict(i) for i in items]

    # Parse datetime string
    try:
        order["created_at"] = datetime.strptime(order["created_at"], "%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    return render_template("order_confirmation.html", order=order, items=items)


# ─── My Orders ───────────────────────────────────────────────
@app.route("/orders")
@login_required
def orders():
    conn = get_db()
    my_orders = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    my_orders = [dict(o) for o in my_orders]

    for o in my_orders:
        items = conn.execute(
            "SELECT oi.quantity, f.name FROM order_items oi "
            "JOIN food_items f ON oi.food_item_id=f.id WHERE oi.order_id=?",
            (o["order_id"],)
        ).fetchall()
        o["items"] = [dict(i) for i in items]
        try:
            o["created_at"] = datetime.strptime(o["created_at"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    return render_template("orders.html", orders=my_orders)


# ─── Placed Orders (Table View) ──────────────────────────────
@app.route("/placed-orders")
@login_required
def placed_orders():
    conn = get_db()
    all_orders = conn.execute(
        "SELECT o.*, u.name AS student_name, u.roll_number, u.email "
        "FROM orders o JOIN users u ON o.user_id=u.id "
        "ORDER BY o.created_at DESC"
    ).fetchall()
    all_orders = [dict(o) for o in all_orders]

    for o in all_orders:
        items = conn.execute(
            "SELECT oi.quantity, oi.unit_price, f.name "
            "FROM order_items oi JOIN food_items f ON oi.food_item_id=f.id "
            "WHERE oi.order_id=?",
            (o["order_id"],)
        ).fetchall()
        o["items"] = [dict(i) for i in items]
        try:
            o["created_at"] = datetime.strptime(o["created_at"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    return render_template("placed_orders.html", orders=all_orders)


# ─── Order Status API ─────────────────────────────────────────
@app.route("/api/order-status/<order_id>")
@login_required
def order_status(order_id):
    conn = get_db()
    row  = conn.execute(
        "SELECT status FROM orders WHERE order_id=? AND user_id=?",
        (order_id, session["user_id"])
    ).fetchone()
    if row:
        return jsonify({"status": row["status"]})
    return jsonify({"error": "Not found"}), 404


# ═══════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn  = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username=?", (username,)
        ).fetchone()

        if admin and check_password_hash(admin["password"], password):
            session["admin_id"]       = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "danger")

    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_id",       None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    conn       = get_db()
    all_orders = conn.execute(
        "SELECT o.*, u.name AS student_name, u.roll_number "
        "FROM orders o JOIN users u ON o.user_id=u.id "
        "ORDER BY o.created_at DESC"
    ).fetchall()
    all_orders = [dict(o) for o in all_orders]

    for o in all_orders:
        items = conn.execute(
            "SELECT oi.quantity, oi.unit_price, f.name "
            "FROM order_items oi JOIN food_items f ON oi.food_item_id=f.id "
            "WHERE oi.order_id=?",
            (o["order_id"],)
        ).fetchall()
        o["items"] = [dict(i) for i in items]
        try:
            o["created_at"] = datetime.strptime(o["created_at"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    pending      = conn.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'").fetchone()[0]
    revenue      = conn.execute(
        "SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status='Completed'"
    ).fetchone()[0]

    return render_template("admin.html",
                           orders=all_orders,
                           total_orders=total_orders,
                           pending=pending,
                           revenue=revenue)


@app.route("/update-order", methods=["POST"])
@admin_required
def update_order():
    data     = request.get_json() or {}
    order_id = data.get("order_id")
    status   = data.get("status")
    allowed  = ["Pending","Accepted","Preparing","Ready","Completed","Cancelled"]
    if status not in allowed:
        return jsonify({"success": False, "message": "Invalid status"}), 400

    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    conn.commit()
    return jsonify({"success": True})


@app.route("/admin/toggle-item/<int:item_id>", methods=["POST"])
@admin_required
def toggle_item(item_id):
    conn = get_db()
    conn.execute(
        "UPDATE food_items SET is_available = CASE WHEN is_available=1 THEN 0 ELSE 1 END "
        "WHERE id=?", (item_id,)
    )
    conn.commit()
    return jsonify({"success": True})


# ─── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n" + "="*55)
    print("  [Smart Canteen Pre-Order System]")
    print("  Running at: http://127.0.0.1:5000")
    print("  Database:   canteen.db  (SQLite)")
    print("  Admin URL:  http://127.0.0.1:5000/admin-login")
    print("  Admin creds: admin / admin123")
    print("="*55 + "\n")
    app.run(debug=True, port=5000)
