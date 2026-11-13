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
    conn.execute("CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, cuisine TEXT, ecocash TEXT, bank_name TEXT, bank_account TEXT, payment_note TEXT)")
    try: conn.execute("ALTER TABLE restaurants ADD COLUMN ecocash TEXT")
    except: pass
    try: conn.execute("ALTER TABLE restaurants ADD COLUMN bank_name TEXT")
    except: pass
    try: conn.execute("ALTER TABLE restaurants ADD COLUMN bank_account TEXT")
    except: pass
    try: conn.execute("ALTER TABLE restaurants ADD COLUMN payment_note TEXT")
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
        cur.execute('SELECT r.name, r.cuisine, r.ecocash, r.bank_name, r.bank_account, r.payment_note, d.dish_name, d.price, d.image FROM restaurants r JOIN dishes d ON r.id = d.restaurant_id')
        data = cur.fetchall()
    except: data = []
    conn.close()
    cards = ""
    if not data: cards = "<h3>No dishes yet - Restaurant owners please add dishes!</h3>"
    for name, cuisine, ecocash, bank_name, bank_acc, note, dish, price, image in data:
        img = f"<img src='{image}' style='width:100%;height:180px;object-fit:cover;border-radius:10px 10px 0 0;'>" if image else "<div style='width:100%;height:180px;background:#eee;line-height:180px;text-align:center;'>No Image</div>"
        pay_info = ""
        if ecocash: pay_info += f"<div style='background:#e8f8e8;padding:5px;margin-top:5px;border-radius:5px;'>📱 EcoCash: <b>{ecocash}</b></div>"
        if bank_name and bank_acc: pay_info += f"<div style='background:#e8e8f8;padding:5px;margin-top:5px;border-radius:5px;'>🏦 {bank_name}: <b>{bank_acc}</b></div>"
        if note: pay_info += f"<div style='font-size:12px;color:#555;margin-top:5px;'><i>{note}</i></div>"
        cards += f"<div style='width:270px;border:1px solid #ddd;border-radius:10px;margin:10px;display:inline-block;vertical-align:top;box-shadow:0 2px 5px #ccc;'>{img}<div style='padding:10px;'><b>{dish}</b> - ${price}<br><small>{name} ({cuisine})</small>{pay_info}<br><button onclick=\"alert('Pay to: {ecocash or bank_acc}. Then WhatsApp owner!')\" style='background:#27ae60;color:white;border:none;padding:8px;width:100%;border-radius:5px;margin-top:5px;'>Pay Now</button></div></div>"
    return f"<html><head><style>body{{font-family:Arial;padding:20px;}}</style></head><body><h1 style='color:#e67e22;'>🍔 ZimMarket</h1><a href='/dashboard'>Dashboard</a> | <a href='/register'>Register Restaurant</a> | <a href='/login'>Login</a><hr><div>{cards}</div></body></html>"

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'restaurant_id' not in session: return redirect('/login')
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    if request.method == 'POST':
        if 'ecocash' in request.form:
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
    cur.execute("SELECT name, ecocash, bank_name, bank_account, payment_note FROM restaurants WHERE id=?", (session['restaurant_id'],))
    owner = cur.fetchone()
    cur.execute("SELECT id, dish_name, price, image FROM dishes WHERE restaurant_id=?", (session['restaurant_id'],))
    my_dishes = cur.fetchall()
    conn.close()
    dishes_html = "".join([f"<div style='border:1px solid #ccc;padding:10px;margin:10px;display:inline-block;width:200px;border-radius:10px;text-align:center;'><img src='{d[3]}' style='width:100%;height:150px;object-fit:cover;border-radius:8px;'><br><b>{d[1]}</b> - ${d[2]}<br><br><a href='/delete/{d[0]}' style='background:red;color:white;padding:5px 10px;text-decoration:none;border-radius:5px;'>Delete</a></div>" for d in my_dishes])
    return f"<h2>Welcome {owner[0]} - Dashboard</h2><div style='display:flex;gap:20px;flex-wrap:wrap;'><div style='background:#fff3cd;padding:20px;border-radius:10px;width:320px;border:1px solid #ffc107;'><h3>💰 Your Payment Portal</h3><form method='POST'><label>EcoCash:</label><br><input type='text' name='ecocash' value='{owner[1] or ''}' placeholder='0771234567' style='width:100%;padding:8px;margin:5px 0;'><br><label>Bank Name:</label><br><input type='text' name='bank_name' value='{owner[2] or ''}' placeholder='CBZ' style='width:100%;padding:8px;margin:5px 0;'><br><label>Account No:</label><br><input type='text' name='bank_account' value='{owner[3] or ''}' placeholder='123456' style='width:100%;padding:8px;margin:5px 0;'><br><label>Instructions:</label><br><textarea name='payment_note' style='width:100%;padding:8px;margin:5px 0;'>{owner[4] or ''}</textarea><br><button style='background:#ffc107;border:none;padding:10px;width:100%;border-radius:5px;font-weight:bold;'>Save Payment</button></form></div><div style='background:#f9f9f9;padding:20px;border-radius:10px;width:320px;'><h3>Add Dish</h3><form method='POST' enctype='multipart/form-data'><input type='text' name='dish' placeholder='Pizza' required style='width:100%;padding:8px;margin:5px 0;'><br><input type='text' name='price' placeholder='12' required style='width:100%;padding:8px;margin:5px 0;'><br><input type='file' name='image' accept='image/*' required style='margin:10px 0;'><br><button style='background:#27ae60;color:white;padding:10px;width:100%;border:none;border-radius:5px;'>Add Dish</button></form></div></div><hr><h3>Your Dishes</h3><div>{dishes_html if dishes_html else 'No dishes'}</div><hr><a href='/logout'>Logout</a> | <a href='/'>Home</a>"

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
    return '<h2>Register Restaurant</h2><form method="POST"><input name="name" placeholder="Restaurant Name" required><br><input name="email" placeholder="Email" required><br><input name="password" placeholder="Password" required><br><input name="cuisine" placeholder="Cuisine" required><br><button>Register</button></form>'

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
    return '<h2>Login</h2><form method="POST"><input name="email"><br><input name="password" type="password"><br><button>Login</button></form>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# SECRET ADMIN - ONLY YOU KNOW THIS URL
@app.route('/zimadmin2026', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('email') == 'admin@zimmarket.com' and request.form.get('password') == 'admin123':
            session['is_admin'] = True
            return redirect('/zimadmin2026/dashboard')
        return "Wrong admin password!"
    return '<h2>ZimMarket SECRET ADMIN</h2><form method="POST"><input name="email" placeholder="admin@zimmarket.com"><br><input name="password" type="password" placeholder="admin123"><br><button>Enter</button></form>'

@app.route('/zimadmin2026/dashboard')
def admin_dashboard():
    if not session.get('is_admin'): return redirect('/zimadmin2026')
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, cuisine, ecocash, bank_account FROM restaurants")
    rests = cur.fetchall()
    cur.execute("SELECT d.id, d.dish_name, d.price, d.image, r.name FROM dishes d JOIN restaurants r ON d.restaurant_id = r.id")
    dishes = cur.fetchall()
    conn.close()
    rest_html = "".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td><a href='/zimadmin2026/delete_rest/{r[0]}' style='color:red;'>DELETE</a></td></tr>" for r in rests])
    dish_html = "".join([f"<tr><td>{d[0]}</td><td><img src='{d[3]}' style='width:50px;height:50px;object-fit:cover;'></td><td>{d[1]}</td><td>${d[2]}</td><td>{d[4]}</td><td><a href='/zimadmin2026/delete_dish/{d[0]}' style='color:red;'>DELETE</a></td></tr>" for d in dishes])
    return f"<h1>👑 SECRET ADMIN - YOU CONTROL EVERYTHING</h1><p>Restaurants: <b>{len(rests)}</b> | Dishes: <b>{len(dishes)}</b></p><a href='/zimadmin2026/logout'>Logout</a> | <a href='/'>Home</a><hr><h2>All Restaurants + Payments</h2><table border=1 cellpadding=10><tr><th>ID</th><th>Name</th><th>Email</th><th>Cuisine</th><th>EcoCash</th><th>Bank</th><th>Action</th></tr>{rest_html}</table><h2>All Dishes</h2><table border=1 cellpadding=10><tr><th>ID</th><th>Image</th><th>Dish</th><th>Price</th><th>Owner</th><th>Action</th></tr>{dish_html}</table>"

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