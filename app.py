from flask import Flask, request, redirect, session
from werkzeug.utils import secure_filename
import os, sqlite3

app = Flask(__name__)
app.secret_key = "zimmarket-secret-2026"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, cuisine TEXT, ecocash TEXT, bank_name TEXT, bank_account TEXT, payment_note TEXT, logo TEXT)")
    for col in ["ecocash","bank_name","bank_account","payment_note","logo"]:
        try: conn.execute(f"ALTER TABLE restaurants ADD COLUMN {col} TEXT")
        except: pass
    conn.execute("CREATE TABLE IF NOT EXISTS dishes (id INTEGER PRIMARY KEY, restaurant_id INTEGER, dish_name TEXT, price TEXT, image TEXT)")
    try: conn.execute("ALTER TABLE dishes ADD COLUMN image TEXT")
    except: pass
    conn.commit(); conn.close()
init_db()

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
        cards = "<div style='text-align:center;padding:50px;'><h3>🍽️ No dishes yet</h3><p>Restaurant owners, add your first dish!</p></div>"
    for name, cuisine, ecocash, bank_name, bank_acc, note, logo, dish, price, image in data:
        logo_html = f"<img src='{logo}' style='width:50px;height:50px;border-radius:50%;object-fit:cover;border:2px solid #e67e22;'>" if logo else f"<div style='width:50px;height:50px;border-radius:50%;background:#e67e22;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:20px;'>{name[0].upper()}</div>"
        img = f"<img src='{image}' style='width:100%;height:200px;object-fit:cover;'>" if image else "<div style='width:100%;height:200px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;'>No Image</div>"
        pay = ""
        if ecocash: pay += f"<div style='background:#e8f5e9;padding:6px;border-radius:6px;margin:4px 0;font-size:13px;'>📱 EcoCash: <b>{ecocash}</b></div>"
        if bank_name and bank_acc: pay += f"<div style='background:#e3f2fd;padding:6px;border-radius:6px;margin:4px 0;font-size:13px;'>🏦 {bank_name}: <b>{bank_acc}</b></div>"
        cards += f"""
        <div style='width:300px;background:white;border-radius:16px;overflow:hidden;margin:15px;display:inline-block;vertical-align:top;box-shadow:0 4px 15px rgba(0,0,0,0.1);transition:transform 0.2s;'>
            {img}
            <div style='padding:15px;'>
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px;'>
                    {logo_html}
                    <div><div style='font-weight:bold;font-size:16px;'>{name}</div><div style='font-size:12px;color:#777;background:#f5f5f5;padding:2px 8px;border-radius:10px;display:inline-block;'>{cuisine}</div></div>
                </div>
                <div style='font-size:18px;font-weight:bold;margin:8px 0;'>{dish}</div>
                <div style='font-size:22px;color:#27ae60;font-weight:bold;'>${price}</div>
                {pay}
                <button onclick="alert('Pay to {name}: {ecocash or bank_acc}\\nThen WhatsApp proof!')" style='background:linear-gradient(135deg,#27ae60,#2ecc71);color:white;border:none;padding:12px;width:100%;border-radius:10px;margin-top:10px;font-weight:bold;font-size:15px;cursor:pointer;'>💳 Pay & Order Now</button>
            </div>
        </div>
        """
    return f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>
    body{{font-family:'Segoe UI',Arial;background:#fafafa;margin:0;padding:0;}}
    .header{{background:white;padding:15px 25px;box-shadow:0 2px 10px rgba(0,0,0,0.05);display:flex;justify-content:space-between;align-items:center;}}
    .logo{{font-size:24px;font-weight:900;color:#e67e22;}}
    .nav a{{text-decoration:none;color:#333;margin-left:15px;font-weight:500;padding:8px 15px;border-radius:20px;}}
    .nav a:hover{{background:#f0f0f0;}}
    .hero{{background:linear-gradient(135deg,#e67e22,#f39c12);color:white;padding:40px 25px;text-align:center;}}
    .container{{padding:20px;text-align:center;}}
    </style></head><body>
    <div class='header'><div class='logo'>🍔 ZimMarket</div><div class='nav'><a href='/dashboard'>Dashboard</a><a href='/register'>Register</a><a href='/login' style='background:#e67e22;color:white;'>Login</a></div></div>
    <div class='hero'><h1 style='margin:0;font-size:36px;'>Delicious Food from Harare</h1><p style='font-size:18px;opacity:0.9;'>Pay with EcoCash • Direct to Restaurant • No middleman</p></div>
    <div class='container'><h2 style='text-align:left;margin-left:15px;'>🔥 All Dishes</h2>{cards}</div>
    </body></html>
    """

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
                if logofile and logofile.filename != '':
                    fname = secure_filename(f"logo_{session['restaurant_id']}_{logofile.filename}")
                    fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                    logofile.save(fpath)
                    logo_url = f"/{fpath}"
            if logo_url:
                cur.execute("UPDATE restaurants SET ecocash=?, bank_name=?, bank_account=?, payment_note=?, logo=? WHERE id=?", (request.form.get('ecocash'), request.form.get('bank_name'), request.form.get('bank_account'), request.form.get('payment_note'), logo_url, session['restaurant_id']))
            else:
                cur.execute("UPDATE restaurants SET ecocash=?, bank_name=?, bank_account=?, payment_note=? WHERE id=?", (request.form.get('ecocash'), request.form.get('bank_name'), request.form.get('bank_account'), request.form.get('payment_note'), session['restaurant_id']))
            conn.commit()
        else:
            file = request.files.get('image')
            image_url = ''
            if file and file.filename != '':
                filename = secure_filename(f"{session['restaurant_id']}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"/{filepath}"
            cur.execute("INSERT INTO dishes (restaurant_id, dish_name, price, image) VALUES (?,?,?,?)", (session['restaurant_id'], request.form.get('dish'), request.form.get('price'), image_url))
            conn.commit()
        conn.close()
        return redirect('/dashboard')
    
    cur.execute("SELECT name, ecocash, bank_name, bank_account, payment_note, logo FROM restaurants WHERE id=?", (session['restaurant_id'],))
    owner = cur.fetchone()
    cur.execute("SELECT id, dish_name, price, image FROM dishes WHERE restaurant_id=?", (session['restaurant_id'],))
    my_dishes = cur.fetchall()
    conn.close()
    
    dishes_html = "".join([f"<div style='background:white;border-radius:12px;overflow:hidden;width:200px;margin:10px;display:inline-block;box-shadow:0 2px 8px #ddd;'><img src='{d[3]}' style='width:100%;height:140px;object-fit:cover;'><div style='padding:10px;'><b>{d[1]}</b><br>${d[2]}<br><a href='/delete/{d[0]}' style='background:#e74c3c;color:white;padding:5px 10px;text-decoration:none;border-radius:5px;font-size:12px;display:inline-block;margin-top:5px;'>Delete</a></div></div>" for d in my_dishes])
    
    logo_preview = f"<img src='{owner[5]}' style='width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid #e67e22;'>" if owner[5] else "<div style='width:80px;height:80px;border-radius:50%;background:#eee;display:flex;align-items:center;justify-content:center;'>No Logo</div>"

    return f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:Arial;padding:20px;background:#fafafa;}}</style></head><body>
    <h2>🍔 {owner[0]} - Beautiful Dashboard</h2>
    <div style='display:flex;gap:20px;flex-wrap:wrap;'>
        <div style='background:white;padding:20px;border-radius:16px;width:340px;box-shadow:0 4px 15px rgba(0,0,0,0.08);'>
            <h3 style='margin-top:0;'>🏪 Restaurant Logo</h3>
            <div style='text-align:center;margin:10px 0;'>{logo_preview}</div>
            <form method='POST' enctype='multipart/form-data'>
                <label><b>Upload Logo (your brand):</b></label><br>
                <input type='file' name='logo' accept='image/*' style='margin:10px 0;'><br>
                <label>EcoCash Number:</label><br>
                <input type='text' name='ecocash' value='{owner[1] or ""}' placeholder='0771234567' style='width:100%;padding:10px;margin:5px 0;border-radius:8px;border:1px solid #ddd;'><br>
                <label>Bank Name:</label><br>
                <input type='text' name='bank_name' value='{owner[2] or ""}' placeholder='CBZ / Steward' style='width:100%;padding:10px;margin:5px 0;border-radius:8px;border:1px solid #ddd;'><br>
                <label>Account No:</label><br>
                <input type='text' name='bank_account' value='{owner[3] or ""}' placeholder='123456789' style='width:100%;padding:10px;margin:5px 0;border-radius:8px;border:1px solid #ddd;'><br>
                <label>Payment Note:</label><br>
                <textarea name='payment_note' style='width:100%;padding:10px;margin:5px 0;border-radius:8px;border:1px solid #ddd;'>{owner[4] or ""}</textarea><br>
                <button style='background:#e67e22;color:white;border:none;padding:12px;width:100%;border-radius:10px;font-weight:bold;margin-top:10px;'>💾 Save Profile & Payments</button>
            </form>
        </div>
        <div style='background:white;padding:20px;border-radius:16px;width:340px;box-shadow:0 4px 15px rgba(0,0,0,0.08);'>
            <h3>Add Beautiful Dish</h3>
            <form method='POST' enctype='multipart/form-data'>
                <input type='text' name='dish' placeholder='e.g. Double Burger' required style='width:100%;padding:10px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
                <input type='text' name='price' placeholder='Price $ e.g. 5.50' required style='width:100%;padding:10px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
                <input type='file' name='image' accept='image/*' required style='margin:10px 0;'><br>
                <button style='background:linear-gradient(135deg,#27ae60,#2ecc71);color:white;padding:12px;width:100%;border:none;border-radius:10px;font-weight:bold;'>➕ Add Dish</button>
            </form>
        </div>
    </div>
    <hr style='margin:25px 0;'><h3>Your Menu ({len(my_dishes)} dishes)</h3><div>{dishes_html if dishes_html else '<p>No dishes yet - add your first!</p>'}</div><hr><a href='/logout'>Logout</a> | <a href='/'>View as Customer</a>
    </body></html>
    """

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
        conn = sqlite3.connect('zimmarket.db')
        try:
            conn.execute("INSERT INTO restaurants (name, email, password, cuisine) VALUES (?,?,?,?)", (request.form.get('name'), request.form.get('email'), request.form.get('password'), request.form.get('cuisine')))
            conn.commit()
        except: pass
        conn.close()
        return redirect('/login')
    return """
    <html><body style='font-family:Arial;display:flex;justify-content:center;padding:40px;background:#fafafa;'><div style='background:white;padding:30px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.1);width:350px;'>
    <h2>Register Your Restaurant</h2><form method="POST">
    <input name="name" placeholder="Restaurant Name e.g. Pibby's" required style='width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
    <input name="email" placeholder="Email" required style='width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
    <input name="password" type="password" placeholder="Password" required style='width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
    <input name="cuisine" placeholder="Cuisine e.g. Fast Food" required style='width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
    <button style='background:#e67e22;color:white;border:none;padding:12px;width:100%;border-radius:10px;font-weight:bold;margin-top:10px;'>Register</button></form></div></body></html>
    """

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('zimmarket.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM restaurants WHERE email=? AND password=?", (request.form.get('email'), request.form.get('password')))
        user = cur.fetchone()
        conn.close()
        if user:
            session['restaurant_id'] = user[0]
            return redirect('/dashboard')
    return """
    <html><body style='font-family:Arial;display:flex;justify-content:center;padding:40px;background:#fafafa;'><div style='background:white;padding:30px;border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.1);width:350px;'>
    <h2>Login</h2><form method="POST">
    <input name="email" placeholder="Email" required style='width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
    <input name="password" type="password" placeholder="Password" required style='width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ddd;'><br>
    <button style='background:#27ae60;color:white;border:none;padding:12px;width:100%;border-radius:10px;font-weight:bold;margin-top:10px;'>Login</button></form></div></body></html>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# SECRET ADMIN - HIDDEN
@app.route('/zimadmin2026', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('email') == 'admin@zimmarket.com' and request.form.get('password') == 'admin123':
            session['is_admin'] = True
            return redirect('/zimadmin2026/dashboard')
        return "Wrong password!"
    return '<h2>SECRET ADMIN</h2><form method="POST"><input name="email"><br><input name="password" type="password"><br><button>Enter</button></form>'

@app.route('/zimadmin2026/dashboard')
def admin_dashboard():
    if not session.get('is_admin'): return redirect('/zimadmin2026')
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, cuisine, ecocash, bank_account, logo FROM restaurants")
    rests = cur.fetchall()
    cur.execute("SELECT d.id, d.dish_name, d.price, d.image, r.name FROM dishes d JOIN restaurants r ON d.restaurant_id = r.id")
    dishes = cur.fetchall()
    conn.close()
    rest_html = "".join([f"<tr><td><img src='{r[6]}' style='width:40px;height:40px;border-radius:50%;object-fit:cover;'></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td><a href='/zimadmin2026/delete_rest/{r[0]}' style='color:red;'>DELETE</a></td></tr>" for r in rests])
    dish_html = "".join([f"<tr><td><img src='{d[3]}' style='width:50px;height:50px;object-fit:cover;'></td><td>{d[1]}</td><td>${d[2]}</td><td>{d[4]}</td><td><a href='/zimadmin2026/delete_dish/{d[0]}' style='color:red;'>DELETE</a></td></tr>" for d in dishes])
    return f"<h1>👑 SECRET ADMIN - BEAUTIFUL CONTROL</h1><p>Restaurants: {len(rests)} | Dishes: {len(dishes)}</p><a href='/zimadmin2026/logout'>Logout</a> | <a href='/'>Home</a><hr><h2>Restaurants with Logos</h2><table border=1 cellpadding=10><tr><th>Logo</th><th>Name</th><th>Email</th><th>Cuisine</th><th>EcoCash</th><th>Bank</th><th>Action</th></tr>{rest_html}</table><h2>Dishes</h2><table border=1 cellpadding=10><tr><th>Image</th><th>Dish</th><th>Price</th><th>Owner</th><th>Action</th></tr>{dish_html}</table>"

@app.route('/zimadmin2026/delete_rest/<int:rest_id>')
def admin_delete_rest(rest_id):
    if not session.get('is_admin'): return redirect('/zimadmin2026')
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("DELETE FROM restaurants WHERE id=?", (rest_id,))
    conn.execute("DELETE FROM dishes WHERE restaurant_id=?", (rest_id,))
    conn.commit(); conn.close()
    return redirect('/zimadmin2026/dashboard')

@app.route('/zimadmin2026/delete_dish/<int:dish_id>')
def admin_delete_dish(dish_id):
    if not session.get('is_admin'): return redirect('/zimadmin2026')
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("DELETE FROM dishes WHERE id=?", (dish_id,))
    conn.commit(); conn.close()
    return redirect('/zimadmin2026/dashboard')

@app.route('/zimadmin2026/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect('/zimadmin2026')

if __name__ == '__main__':
    app.run(debug=True)