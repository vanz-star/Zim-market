from flask import Flask, render_template_string, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "zimmarket-secret-2026"

def init_db():
    conn = sqlite3.connect('zimmarket.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS restaurants 
    (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, cuisine TEXT, phone TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS dishes 
    (id INTEGER PRIMARY KEY, restaurant_id INTEGER, dish_name TEXT, price TEXT)''')
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT r.name, r.cuisine, d.dish_name, d.price FROM restaurants r JOIN dishes d ON r.id=d.restaurant_id")
    data = cur.fetchall()
    conn.close()
    cards = ""
    if not data:
        cards = "<p style='text-align:center;padding:40px'>No restaurants yet. Be first! <br><br><a href='/register' style='background:#2E7D32;color:white;padding:12px 20px;border-radius:10px;text-decoration:none'>Register Restaurant</a></p>"
    for name, cuisine, dish, price in data:
        flag = "🇿🇼" if "Traditional" in cuisine else "🇮🇹" if "Italian" in cuisine else "🇲🇽" if "Mexican" in cuisine else "🍽️"
        cards += f'<div class="card"><div class="top"><span>🍛</span><span class="badge">{flag} {cuisine}</span></div><h3>{name}</h3><p>{dish}</p><div class="row"><span class="price">{price}</span><button class="btn">Order</button></div></div>'
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{{font-family:Arial;margin:0;background:#f5f5f5}} .header{{background:#111;color:white;padding:18px;text-align:center}} .container{{max-width:600px;margin:auto;padding:12px}} .card{{background:white;border-radius:16px;padding:15px;margin:12px 0;box-shadow:0 2px 8px rgba(0,0,0,.08)}} .top{{display:flex;justify-content:space-between}} .badge{{background:#eee;padding:4px 10px;border-radius:12px;font-size:12px}} .row{{display:flex;justify-content:space-between;align-items:center}} .price{{color:#e65100;font-weight:bold}} .btn{{background:#2E7D32;color:white;border:none;padding:8px 16px;border-radius:8px}} .nav{{display:flex;gap:10px;justify-content:center;padding:10px}} .nav a{{text-decoration:none;background:white;padding:8px 14px;border-radius:20px;border:1px solid #ddd;color:#111;font-size:13px}}</style></head><body><div class='header'><h1 style='margin:0'>ZimMarket</h1><small>Harare Food Marketplace</small><div class='nav'><a href='/'>🏠 Home</a><a href='/register'>➕ Register</a><a href='/login'>🔑 Login</a></div></div><div class='container'>{cards}</div></body></html>"

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('zimmarket.db')
            conn.execute("INSERT INTO restaurants (name,email,password,cuisine,phone) VALUES (?,?,?,?,?)",(request.form['name'], request.form['email'], request.form['password'], request.form['cuisine'], request.form['phone']))
            conn.commit(); conn.close()
            return redirect('/login')
        except: return "Email used! <a href='/register'>Try again</a>"
    return "<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{font-family:Arial;background:#f5f5f5;padding:20px} .box{max-width:400px;margin:auto;background:white;padding:20px;border-radius:16px} input,select{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;box-sizing:border-box} button{width:100%;padding:12px;background:#111;color:white;border:none;border-radius:8px;font-weight:bold}</style></head><body><div class='box'><h2>Register Restaurant</h2><form method='POST'><input name='name' placeholder='Restaurant Name' required><select name='cuisine' required><option value=''>Cuisine</option><option>Traditional</option><option>Italian</option><option>Mexican</option><option>Mixed</option></select><input name='email' type='email' placeholder='Email' required><input name='phone' placeholder='Phone' required><input name='password' type='password' placeholder='Password' required><button type='submit'>Register</button></form><p><a href='/'>Back</a></p></div></body></html>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('zimmarket.db')
        cur = conn.cursor()
        cur.execute("SELECT id,name FROM restaurants WHERE email=? AND password=?", (request.form['email'], request.form['password']))
        row = cur.fetchone(); conn.close()
        if row:
            session['rest_id']=row[0]; session['rest_name']=row[1]
            return redirect('/dashboard')
        else: return "Wrong password <a href='/login'>Try again</a>"
    return "<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{font-family:Arial;background:#f5f5f5;padding:20px} .box{max-width:400px;margin:auto;background:white;padding:20px;border-radius:16px} input{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px} button{width:100%;padding:12px;background:#2E7D32;color:white;border:none;border-radius:8px;font-weight:bold}</style></head><body><div class='box'><h2>Restaurant Login</h2><form method='POST'><input name='email' placeholder='Email' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><p><a href='/'>Back</a> | <a href='/register'>Register</a></p></div></body></html>"

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'rest_id' not in session: return redirect('/login')
    conn = sqlite3.connect('zimmarket.db')
    if request.method == 'POST':
        conn.execute("INSERT INTO dishes (restaurant_id,dish_name,price) VALUES (?,?,?)",(session['rest_id'], request.form['dish'], request.form['price']))
        conn.commit()
    cur = conn.cursor()
    cur.execute("SELECT dish_name,price FROM dishes WHERE restaurant_id=?", (session['rest_id'],))
    dishes = cur.fetchall(); conn.close()
    list_dishes = "".join([f"<li>{d[0]} - {d[1]}</li>" for d in dishes]) or "<li>No dishes</li>"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{{font-family:Arial;background:#f5f5f5;padding:15px}} .box{{max-width:500px;margin:auto;background:white;padding:20px;border-radius:16px}} input{{width:100%;padding:10px;margin:6px 0;border:1px solid #ddd;border-radius:8px}} button{{padding:10px 16px;background:#111;color:white;border:none;border-radius:8px}}</style></head><body><div class='box'><h2>Welcome {session['rest_name']}!</h2><form method='POST'><input name='dish' placeholder='Dish e.g. Pizza' required><input name='price' placeholder='Price e.g. $12' required><button>Add Dish</button></form><h3>Your Dishes:</h3><ul>{list_dishes}</ul><p><a href='/'>Marketplace</a> | <a href='/logout'>Logout</a></p></div></body></html>"

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=10000)
