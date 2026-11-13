from flask import Flask, request, redirect, session, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os, sqlite3, secrets, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXT = {'png','jpg','jpeg','webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ADMIN_PATH = os.environ.get("ADMIN_PATH", "zimadmin2026")

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

def init_db():
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, cuisine TEXT, ecocash TEXT, bank_name TEXT, bank_account TEXT, payment_note TEXT, logo TEXT, created_at TEXT)")
    for col in ["ecocash","bank_name","bank_account","payment_note","logo","created_at"]:
        try: conn.execute(f"ALTER TABLE restaurants ADD COLUMN {col} TEXT")
        except: pass
    conn.execute("CREATE TABLE IF NOT EXISTS dishes (id INTEGER PRIMARY KEY, restaurant_id INTEGER, dish_name TEXT, price TEXT, image TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, dish_id INTEGER, restaurant_id INTEGER, customer_name TEXT, customer_phone TEXT, status TEXT, created_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS admin_notifications (id INTEGER PRIMARY KEY, type TEXT, message TEXT, created_at TEXT, is_read INTEGER DEFAULT 0)")
    try: conn.execute("ALTER TABLE orders ADD COLUMN customer_name TEXT")
    except: pass
    try: conn.execute("ALTER TABLE orders ADD COLUMN customer_phone TEXT")
    except: pass
    conn.commit(); conn.close()
init_db()

def add_notification(type_, message):
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("INSERT INTO admin_notifications (type, message, created_at) VALUES (?,?,?)", (type_, message, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

def sanitize(text):
    if not text: return ""
    return re.sub(r'[<>\"\'\;]', '', text)[:200]

@app.route('/')
def home():
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute('SELECT r.id, r.name, r.cuisine, r.ecocash, r.bank_name, r.bank_account, r.logo, d.id, d.dish_name, d.price, d.image FROM restaurants r JOIN dishes d ON r.id = d.restaurant_id')
    data = cur.fetchall()
    conn.close()
    cards = ""
    if not data:
        cards = "<div style='text-align:center;padding:50px;'><h3>🍽️ No dishes yet</h3></div>"
    for rest_id, rname, cuisine, ecocash, bank_name, bank_acc, logo, dish_id, dish_name, price, image in data:
        logo_html = f"<img src='{logo}' style='width:50px;height:50px;border-radius:50%;object-fit:cover;border:2px solid #e67e22;'>" if logo else f"<div style='width:50px;height:50px;border-radius:50%;background:#e67e22;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;'>{sanitize(rname)[0].upper()}</div>"
        img = f"<img src='{image}' style='width:100%;height:200px;object-fit:cover;'>" if image else "<div style='width:100%;height:200px;background:#f0f0f0;'></div>"
        cards += f"""
        <div style='width:300px;background:white;border-radius:16px;overflow:hidden;margin:15px;display:inline-block;vertical-align:top;box-shadow:0 4px 15px rgba(0,0,0,0.1);'>
            {img}
            <div style='padding:15px;'>
                <div style='display:flex;align-items:center;gap:10px;'><div>{logo_html}</div><div><div style='font-weight:bold;'>{sanitize(rname)}</div><div style='font-size:12px;color:#777;'>{sanitize(cuisine)}</div></div></div>
                <div style='font-size:18px;font-weight:bold;margin:8px 0;'>{sanitize(dish_name)}</div>
                <div style='font-size:22px;color:#27ae60;font-weight:bold;'>${sanitize(price)}</div>
                <form method='POST' action='/order/{dish_id}' style='margin-top:10px;'>
                    <input name='cust_name' placeholder='Your Name' required style='width:100%;padding:8px;margin:3px 0;border-radius:6px;border:1px solid #ddd;'>
                    <input name='cust_phone' placeholder='Your Phone 077...' required style='width:100%;padding:8px;margin:3px 0;border-radius:6px;border:1px solid #ddd;'>
                    <button style='background:linear-gradient(135deg,#27ae60,#2ecc71);color:white;border:none;padding:10px;width:100%;border-radius:8px;font-weight:bold;margin-top:5px;'>🛒 Order Now</button>
                </form>
                <div style='font-size:11px;color:#888;margin-top:5px;'>Pay: EcoCash {sanitize(ecocash) if ecocash else 'N/A'}</div>
            </div>
        </div>
        """
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:Arial;background:#fafafa;margin:0;}}.header{{background:white;padding:15px 25px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 5px #eee;}}</style></head><body><div class='header'><div style='font-weight:900;color:#e67e22;font-size:22px;'>🍔 ZimMarket</div><div><a href='/my_orders' style='background:#e67e22;color:white;padding:8px 15px;border-radius:20px;text-decoration:none;'>My Orders</a> <a href='/dashboard'>Dashboard</a> <a href='/register'>Register</a> <a href='/login'>Login</a></div></div><div style='background:linear-gradient(135deg,#e67e22,#f39c12);color:white;padding:25px;text-align:center;'><h1>Order • Pay EcoCash • Cancel Anytime</h1></div><div style='padding:20px;text-align:center;'>{cards}</div></body></html>"

@app.route('/order/<int:dish_id>', methods=['POST'])
def place_order(dish_id):
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT restaurant_id FROM dishes WHERE id=?", (dish_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return "Dish not found", 404
    restaurant_id = row[0]
    cust_name = sanitize(request.form.get('cust_name'))
    cust_phone = sanitize(request.form.get('cust_phone'))
    cur.execute("INSERT INTO orders (dish_id, restaurant_id, customer_name, customer_phone, status, created_at) VALUES (?,?,?,?,?,?)", (dish_id, restaurant_id, cust_name, cust_phone, "PENDING", datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    # Save order in session so customer can see My Orders
    if 'my_order_ids' not in session:
        session['my_order_ids'] = []
    my_ids = session['my_order_ids']
    my_ids.append(order_id)
    session['my_order_ids'] = my_ids
    add_notification("NEW ORDER", f"Order #{order_id} for dish {dish_id} by {cust_name} ({cust_phone})")
    return redirect('/my_orders')

@app.route('/my_orders')
def my_orders():
    order_ids = session.get('my_order_ids', [])
    if not order_ids:
        return "<html><body style='font-family:Arial;padding:20px;'><h2>📦 My Orders</h2><p>No orders yet. Go to <a href='/'>Home</a> to order.</p></body></html>"
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    q_marks = ','.join('?' for _ in order_ids)
    cur.execute(f"SELECT o.id, o.status, o.created_at, d.dish_name, d.price, d.image, r.name FROM orders o JOIN dishes d ON o.dish_id = d.id JOIN restaurants r ON o.restaurant_id = r.id WHERE o.id IN ({q_marks}) ORDER BY o.id DESC", order_ids)
    orders = cur.fetchall()
    conn.close()
    html = ""
    for oid, status, created, dname, price, img, rname in orders:
        status_color = "#27ae60" if status=="PENDING" else "#e74c3c" if status=="CANCELLED" else "#3498db"
        cancel_btn = f"<a href='/cancel_order/{oid}' style='background:#e74c3c;color:white;padding:8px 15px;border-radius:6px;text-decoration:none;display:inline-block;margin-top:8px;' onclick=\"return confirm('Cancel this order?')\">❌ Cancel This Order</a>" if status=="PENDING" else f"<div style='color:{status_color};font-weight:bold;margin-top:8px;'>{status}</div>"
        html += f"<div style='background:white;border-radius:12px;padding:15px;margin:15px;width:320px;display:inline-block;box-shadow:0 2px 10px #ddd;vertical-align:top;'><img src='{img}' style='width:100%;height:150px;object-fit:cover;border-radius:8px;'><div style='margin-top:10px;'><b>{sanitize(dname)}</b> - ${sanitize(price)}<br><small>From: {sanitize(rname)}</small><br><small>Order #{oid} • {created}</small><br><div style='background:{status_color};color:white;padding:4px 8px;border-radius:10px;display:inline-block;font-size:12px;margin-top:5px;'>{status}</div><br>{cancel_btn}</div></div>"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'></head><body style='font-family:Arial;background:#fafafa;padding:20px;'><h2>📦 My Orders - You can cancel anytime before delivery</h2><a href='/' style='background:#333;color:white;padding:8px 15px;border-radius:20px;text-decoration:none;'>← Back to Menu</a><div style='margin-top:20px;'>{html}</div></body></html>"

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    if order_id not in session.get('my_order_ids', []):
        return "You can only cancel your own orders!", 403
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT status FROM orders WHERE id=?", (order_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return "Order not found", 404
    if row[0] != "PENDING":
        conn.close()
        return f"Cannot cancel, already {row[0]}", 400
    cur.execute("UPDATE orders SET status='CANCELLED' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    add_notification("ORDER CANCELLED", f"Customer cancelled Order #{order_id}")
    return redirect('/my_orders')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'restaurant_id' not in session: return redirect('/login')
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    if request.method == 'POST':
        if 'ecocash' in request.form or 'logo' in request.files:
            logo_url = None
            if 'logo' in request.files:
                logofile = request.files.get('logo')
                if logofile and logofile.filename != '' and is_allowed_file(logofile.filename):
                    fname = secure_filename(f"logo_{session['restaurant_id']}_{logofile.filename}")
                    fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                    logofile.save(fpath)
                    logo_url = f"/{fpath}"
            if logo_url:
                cur.execute("UPDATE restaurants SET ecocash=?, bank_name=?, bank_account=?, payment_note=?, logo=? WHERE id=?", (sanitize(request.form.get('ecocash')), sanitize(request.form.get('bank_name')), sanitize(request.form.get('bank_account')), sanitize(request.form.get('payment_note')), logo_url, session['restaurant_id']))
            else:
                cur.execute("UPDATE restaurants SET ecocash=?, bank_name=?, bank_account=?, payment_note=? WHERE id=?", (sanitize(request.form.get('ecocash')), sanitize(request.form.get('bank_name')), sanitize(request.form.get('bank_account')), sanitize(request.form.get('payment_note')), session['restaurant_id']))
            conn.commit()
        else:
            file = request.files.get('image')
            image_url = ''
            if file and file.filename != '' and is_allowed_file(file.filename):
                filename = secure_filename(f"{session['restaurant_id']}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"/{filepath}"
                cur.execute("INSERT INTO dishes (restaurant_id, dish_name, price, image) VALUES (?,?,?,?)", (session['restaurant_id'], sanitize(request.form.get('dish')), sanitize(request.form.get('price')), image_url))
                conn.commit()
        conn.close()
        return redirect('/dashboard')
    cur.execute("SELECT name, ecocash, bank_name, bank_account, payment_note, logo FROM restaurants WHERE id=?", (session['restaurant_id'],))
    owner = cur.fetchone()
    cur.execute("SELECT id, dish_name, price, image FROM dishes WHERE restaurant_id=?", (session['restaurant_id'],))
    my_dishes = cur.fetchall()
    # ORDERS FOR THIS RESTAURANT
    cur.execute("SELECT o.id, o.customer_name, o.customer_phone, o.status, o.created_at, d.dish_name, d.price FROM orders o JOIN dishes d ON o.dish_id = d.id WHERE o.restaurant_id=? ORDER BY o.id DESC LIMIT 30", (session['restaurant_id'],))
    my_orders = cur.fetchall()
    conn.close()
    dishes_html = "".join([f"<div style='background:white;border-radius:12px;width:180px;margin:10px;display:inline-block;'><img src='{d[3]}' style='width:100%;height:120px;object-fit:cover;'><div style='padding:8px;'><b>{sanitize(d[1])}</b><br>${sanitize(d[2])}<br><a href='/delete/{d[0]}' style='color:red;'>Delete</a></div></div>" for d in my_dishes])
    orders_html = ""
    for oid, cname, cphone, status, created, dname, price in my_orders:
        color = "#27ae60" if status=="PENDING" else "#e74c3c"
        orders_html += f"<tr><td>#{oid}</td><td>{sanitize(dname)} ${sanitize(price)}</td><td>{sanitize(cname)}<br>{sanitize(cphone)}</td><td><span style='background:{color};color:white;padding:3px 8px;border-radius:10px;font-size:12px;'>{status}</span></td><td>{created}</td></tr>"
    logo_preview = f"<img src='{owner[5]}' style='width:60px;height:60px;border-radius:50%;'>" if owner[5] else "No Logo"
    return f"<html><body style='font-family:Arial;padding:20px;background:#fafafa;'><h2>{sanitize(owner[0])} Dashboard</h2><div style='display:flex;gap:15px;flex-wrap:wrap;'><div style='background:white;padding:15px;border-radius:12px;width:320px;'><h3>Logo & Payments</h3>{logo_preview}<form method='POST' enctype='multipart/form-data'><input type='file' name='logo' accept='image/*'><br><input name='ecocash' value='{owner[1] or ''}' placeholder='EcoCash'><br><input name='bank_name' value='{owner[2] or ''}' placeholder='Bank'><br><input name='bank_account' value='{owner[3] or ''}' placeholder='Account'><br><textarea name='payment_note'>{owner[4] or ''}</textarea><br><button>Save</button></form></div><div style='background:white;padding:15px;border-radius:12px;width:320px;'><h3>Add Dish</h3><form method='POST' enctype='multipart/form-data'><input name='dish' required placeholder='Dish'><input name='price' required placeholder='Price'><input type='file' name='image' accept='image/*' required><button>Add</button></form></div></div><hr><h3>📦 Incoming Orders - Customers can cancel</h3><table border=1 cellpadding=8 style='width:100%;background:white;'><tr><th>Order</th><th>Dish</th><th>Customer</th><th>Status</th><th>Time</th></tr>{orders_html if orders_html else '<tr><td colspan=5>No orders yet</td></tr>'}</table><hr><h3>Your Menu</h3>{dishes_html}<hr><a href='/logout'>Logout</a> | <a href='/'>Home</a></body></html>"

@app.route('/delete/<int:dish_id>')
def delete_dish(dish_id):
    if 'restaurant_id' not in session: return redirect('/login')
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("DELETE FROM dishes WHERE id=? AND restaurant_id=?", (dish_id, session['restaurant_id']))
    conn.commit(); conn.close()
    return redirect('/dashboard')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = sanitize(request.form.get('email')).lower()
        hashed = generate_password_hash(request.form.get('password'))
        conn = sqlite3.connect('zimmarket.db')
        try:
            conn.execute("INSERT INTO restaurants (name, email, password, cuisine, created_at) VALUES (?,?,?,?,?)", (sanitize(request.form.get('name')), email, hashed, sanitize(request.form.get('cuisine')), datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            add_notification("NEW RESTAURANT", f"Registered: {request.form.get('name')} - {email}")
        except: 
            conn.close()
            return "Email exists", 400
        conn.close()
        return redirect('/login')
    return '<h2>Register</h2><form method="POST"><input name="name" required><input name="email" required><input name="password" type="password" required><input name="cuisine" required><button>Register</button></form>'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = sanitize(request.form.get('email')).lower()
        conn = sqlite3.connect('zimmarket.db')
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM restaurants WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user[1], request.form.get('password')):
            session['restaurant_id'] = user[0]
            return redirect('/dashboard')
        return "Invalid login", 401
    return '<h2>Login</h2><form method="POST"><input name="email"><input name="password" type="password"><button>Login</button></form>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# SECRET ADMIN
@app.route(f'/{ADMIN_PATH}', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@zimmarket.com")
        admin_pass = os.environ.get("ADMIN_PASS", "admin123")
        if request.form.get('email') == admin_email and request.form.get('password') == admin_pass:
            session['is_admin'] = True
            return redirect(f'/{ADMIN_PATH}/dashboard')
        return "Wrong admin", 403
    return '<h2>SECRET ADMIN</h2><form method="POST"><input name="email"><input name="password" type="password"><button>Enter</button></form>'

@app.route(f'/{ADMIN_PATH}/dashboard')
def admin_dashboard():
    if not session.get('is_admin'): return redirect(f'/{ADMIN_PATH}')
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, cuisine, ecocash, created_at FROM restaurants")
    rests = cur.fetchall()
    cur.execute("SELECT d.id, d.dish_name, d.price, r.name FROM dishes d JOIN restaurants r ON d.restaurant_id = r.id")
    dishes = cur.fetchall()
    cur.execute("SELECT o.id, o.customer_name, o.customer_phone, o.status, o.created_at, d.dish_name, r.name FROM orders o JOIN dishes d ON o.dish_id = d.id JOIN restaurants r ON o.restaurant_id = r.id ORDER BY o.id DESC LIMIT 100")
    orders = cur.fetchall()
    cur.execute("SELECT id, type, message, created_at FROM admin_notifications ORDER BY id DESC LIMIT 50")
    notifs = cur.fetchall()
    conn.close()
    notif_html = "".join([f"<tr><td>{n[0]}</td><td><b>{n[1]}</b></td><td>{n[2]}</td><td>{n[3]}</td></tr>" for n in notifs])
    orders_html = "".join([f"<tr><td>#{o[0]}</td><td>{o[5]} - {o[6]}</td><td>{o[1]} {o[2]}</td><td>{o[3]}</td><td>{o[4]}</td></tr>" for o in orders])
    return f"<html><body style='font-family:Arial;padding:20px;'><h1>👑 SECURE ADMIN</h1><h2>🔔 Notifications (ONLY YOU)</h2><table border=1 cellpadding=8><tr><th>ID</th><th>Type</th><th>Message</th><th>Time</th></tr>{notif_html}</table><h2>All Orders (including Cancelled)</h2><table border=1 cellpadding=8><tr><th>Order</th><th>Dish/Restaurant</th><th>Customer</th><th>Status</th><th>Time</th></tr>{orders_html}</table><hr><a href='/{ADMIN_PATH}/logout'>Logout</a> | <a href='/'>Home</a></body></html>"

@app.route(f'/{ADMIN_PATH}/logout')
def admin_logout():
    session.clear()
    return redirect(f'/{ADMIN_PATH}')

if __name__ == '__main__':
    app.run(debug=False)