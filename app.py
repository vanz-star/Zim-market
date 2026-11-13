from flask import Flask, request, redirect, session, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os, sqlite3, secrets, re
from datetime import datetime

app = Flask(__name__)
# SECURE: Secret key from env, fallback random
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXT = {'png','jpg','jpeg','webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5MB max
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ADMIN ONLY secret route - change this anytime, only you know
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
    try: conn.execute("ALTER TABLE dishes ADD COLUMN image TEXT")
    except: pass
    # NOTIFICATIONS TABLE - ONLY ADMIN SEES
    conn.execute("CREATE TABLE IF NOT EXISTS admin_notifications (id INTEGER PRIMARY KEY, type TEXT, message TEXT, created_at TEXT, is_read INTEGER DEFAULT 0)")
    conn.commit(); conn.close()
init_db()

def add_notification(type_, message):
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("INSERT INTO admin_notifications (type, message, created_at) VALUES (?,?,?)", (type_, message, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

# SECURITY: Block suspicious inputs
def sanitize(text):
    if not text: return ""
    return re.sub(r'[<>\"\'\;]', '', text)[:200]

@app.route('/')
def home():
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    try:
        cur.execute('SELECT r.name, r.cuisine, r.ecocash, r.bank_name, r.bank_account, r.payment_note, r.logo, d.dish_name, d.price, d.image FROM restaurants r JOIN dishes d ON r.id = d.restaurant_id')
        data = cur.fetchall()
    except: data = []
    conn.close()
    cards = ""
    if not data:
        cards = "<div style='text-align:center;padding:50px;'><h3>🍽️ No dishes yet</h3></div>"
    for name, cuisine, ecocash, bank_name, bank_acc, note, logo, dish, price, image in data:
        logo_html = f"<img src='{logo}' style='width:50px;height:50px;border-radius:50%;object-fit:cover;border:2px solid #e67e22;'>" if logo else f"<div style='width:50px;height:50px;border-radius:50%;background:#e67e22;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:20px;'>{sanitize(name)[0].upper()}</div>"
        img = f"<img src='{sanitize(image)}' style='width:100%;height:200px;object-fit:cover;'>" if image else "<div style='width:100%;height:200px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;'>No Image</div>"
        pay = ""
        if ecocash: pay += f"<div style='background:#e8f5e9;padding:6px;border-radius:6px;margin:4px 0;font-size:13px;'>📱 EcoCash: <b>{sanitize(ecocash)}</b></div>"
        if bank_name and bank_acc: pay += f"<div style='background:#e3f2fd;padding:6px;border-radius:6px;margin:4px 0;font-size:13px;'>🏦 {sanitize(bank_name)}: <b>{sanitize(bank_acc)}</b></div>"
        cards += f"<div style='width:300px;background:white;border-radius:16px;overflow:hidden;margin:15px;display:inline-block;vertical-align:top;box-shadow:0 4px 15px rgba(0,0,0,0.1);'>{img}<div style='padding:15px;'><div style='display:flex;align-items:center;gap:10px;'><div>{logo_html}</div><div><div style='font-weight:bold;'>{sanitize(name)}</div><div style='font-size:12px;color:#777;'>{sanitize(cuisine)}</div></div></div><div style='font-size:18px;font-weight:bold;margin:8px 0;'>{sanitize(dish)}</div><div style='font-size:22px;color:#27ae60;font-weight:bold;'>${sanitize(price)}</div>{pay}<button onclick=\"alert('Pay to {sanitize(name)}')\" style='background:#27ae60;color:white;border:none;padding:12px;width:100%;border-radius:10px;margin-top:10px;font-weight:bold;'>💳 Pay Now</button></div></div>"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:Arial;background:#fafafa;margin:0;}}.header{{background:white;padding:15px 25px;display:flex;justify-content:space-between;}}</style></head><body><div class='header'><div style='font-weight:900;color:#e67e22;'>🍔 ZimMarket</div><div><a href='/dashboard'>Dashboard</a> | <a href='/register'>Register</a> | <a href='/login'>Login</a></div></div><div style='background:linear-gradient(135deg,#e67e22,#f39c12);color:white;padding:30px;text-align:center;'><h1>Delicious Food from Harare</h1><p>Secure • EcoCash • Direct Pay</p></div><div style='padding:20px;text-align:center;'>{cards}</div></body></html>"

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
            add_notification("UPDATE", f"Restaurant ID {session['restaurant_id']} updated payment/logo")
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
                add_notification("NEW DISH", f"New dish '{request.form.get('dish')}' by restaurant {session['restaurant_id']}")
            else:
                conn.close()
                return "Invalid image! Only png,jpg,jpeg,webp allowed, max 5MB", 400
        conn.close()
        return redirect('/dashboard')
    cur.execute("SELECT name, ecocash, bank_name, bank_account, payment_note, logo FROM restaurants WHERE id=?", (session['restaurant_id'],))
    owner = cur.fetchone()
    cur.execute("SELECT id, dish_name, price, image FROM dishes WHERE restaurant_id=?", (session['restaurant_id'],))
    my_dishes = cur.fetchall()
    conn.close()
    dishes_html = "".join([f"<div style='background:white;border-radius:12px;width:200px;margin:10px;display:inline-block;box-shadow:0 2px 8px #ddd;'><img src='{d[3]}' style='width:100%;height:140px;object-fit:cover;'><div style='padding:10px;'><b>{sanitize(d[1])}</b><br>${sanitize(d[2])}<br><a href='/delete/{d[0]}' style='color:red;'>Delete</a></div></div>" for d in my_dishes])
    logo_preview = f"<img src='{owner[5]}' style='width:80px;height:80px;border-radius:50%;object-fit:cover;'>" if owner[5] else "No Logo"
    return f"<h2>{sanitize(owner[0])} Dashboard - SECURE</h2><div style='display:flex;gap:20px;flex-wrap:wrap;'><div style='background:white;padding:20px;border-radius:16px;width:340px;'><h3>🏪 Logo & Payments</h3><div style='text-align:center;'>{logo_preview}</div><form method='POST' enctype='multipart/form-data'><input type='file' name='logo' accept='image/*'><br><input type='text' name='ecocash' value='{owner[1] or ''}' placeholder='EcoCash' style='width:100%;padding:10px;margin:5px 0;'><br><input type='text' name='bank_name' value='{owner[2] or ''}' placeholder='Bank' style='width:100%;padding:10px;margin:5px 0;'><br><input type='text' name='bank_account' value='{owner[3] or ''}' placeholder='Account' style='width:100%;padding:10px;margin:5px 0;'><br><textarea name='payment_note' style='width:100%;'>{owner[4] or ''}</textarea><br><button>Save</button></form></div><div style='background:white;padding:20px;border-radius:16px;width:340px;'><h3>Add Dish</h3><form method='POST' enctype='multipart/form-data'><input name='dish