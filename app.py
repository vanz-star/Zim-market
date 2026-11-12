from flask import Flask, request, redirect, session
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "zimmarket-secret-2026"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, cuisine TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS dishes (id INTEGER PRIMARY KEY, restaurant_id INTEGER, dish_name TEXT, price TEXT, image TEXT)")
    conn.commit()
    conn.close()
init_db()

# HOME - NICE PICTURES
@app.route('/')
def home():
    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    try:
        cur.execute('SELECT r.name, r.cuisine, d.dish_name, d.price, d.image FROM restaurants r JOIN dishes d ON r.id = d.restaurant_id')
        data = cur.fetchall()
    except:
        data = []
    conn.close()
    
    cards = ""
    if not data:
        cards = "<h3>No dishes yet - Restaurant owners please add dishes!</h3>"
    
    for name, cuisine, dish, price, image in data:
        img_tag = f"<img src='{image}' style='width:100%;height:180px;object-fit:cover;border-radius:10px 10px 0 0;'>" if image else "<div style='width:100%;height:180px;background:#eee;line-height:180px;text-align:center;'>No Image</div>"
        cards += f"""
        <div style='width:250px;border:1px solid #ddd;border-radius:10px;margin:10px;display:inline-block;vertical-align:top;box-shadow:0 2px 5px #ccc;'>
            {img_tag}
            <div style='padding:10px;'>
                <b>{dish}</b> - ${price}<br>
                <small>{name} ({cuisine})</small>
            </div>
        </div>
        """

    return f"""
    <html><head><style>body{{font-family:Arial;padding:20px;}}</style></head><body>
    <h1 style='color:#e67e22;'>🍔 ZimMarket</h1>
    <a href='/dashboard'>Dashboard</a> | <a href='/register'>Register Restaurant</a> | <a href='/login'>Login</a>
    <hr>
    <div>{cards}</div>
    </body></html>
    """

# DASHBOARD WITH DELETE
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'restaurant_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        dish_name = request.form.get('dish')
        price = request.form.get('price')
        file = request.files.get('image')
        image_url = ''
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filename = f"{session['restaurant_id']}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = f"/{filepath}"
        conn = sqlite3.connect('zimmarket.db')
        conn.execute("INSERT INTO dishes (restaurant_id, dish_name, price, image) VALUES (?,?,?,?)", (session['restaurant_id'], dish_name, price, image_url))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    conn = sqlite3.connect('zimmarket.db')
    cur = conn.cursor()
    cur.execute("SELECT id, dish_name, price, image FROM dishes WHERE restaurant_id=?", (session['restaurant_id'],))
    my_dishes = cur.fetchall()
    conn.close()
    
    dishes_html = ""
    for d_id, d_name, d_price, d_image in my_dishes:
        dishes_html += f"""
        <div style='border:1px solid #ccc;padding:10px;margin:10px;display:inline-block;width:200px;border-radius:10px;text-align:center;'>
            <img src='{d_image}' style='width:100%;height:150px;object-fit:cover;border-radius:8px;'><br>
            <b>{d_name}</b> - ${d_price}<br><br>
            <a href='/delete/{d_id}' style='background:red;color:white;padding:5px 10px;text-decoration:none;border-radius:5px;' onclick="return confirm('Delete this dish?')">Delete</a>
        </div>
        """

    return f"""
    <h2>Add New Dish with Picture</h2>
    <form method="POST" enctype="multipart/form-data" style='background:#f9f9f9;padding:20px;border-radius:10px;width:300px;'>
        <input type="text" name="dish" placeholder="e.g. Pizza" required style='width:100%;padding:8px;margin:5px 0;'><br>
        <input type="text" name="price" placeholder="e.g. 12" required style='width:100%;padding:8px;margin:5px 0;'><br>
        <input type="file" name="image" accept="image/*" required style='margin:10px 0;'><br>
        <button type="submit" style='background:#27ae60;color:white;padding:10px;width:100%;border:none;border-radius:5px;'>Add Dish</button>
    </form>
    <hr><h3>Your Dishes (You can delete)</h3>
    <div>{dishes_html if dishes_html else "No dishes yet"}</div>
    <hr><a href="/logout">Logout</a> | <a href="/">View Customer Home</a>
    """

@app.route('/delete/<int:dish_id>')
def delete_dish(dish_id):
    if 'restaurant_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect('zimmarket.db')
    conn.execute("DELETE FROM dishes WHERE id=? AND restaurant_id=?", (dish_id, session['restaurant_id']))
    conn.commit()
    conn.close()
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
    return '<h2>Register Restaurant</h2><form method="POST"><input name="name" placeholder="Restaurant Name" required><br><input name="email" placeholder="Email" required><br><input name="password" placeholder="Password" required><br><input name="cuisine" placeholder="Cuisine e.g. Italian" required><br><button>Register</button></form>'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('zimmarket.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM restaurants WHERE email=? AND password=?", (request.form.get('email'), request.form.get('password')))
        user = cur.fetchone()
        conn.close()
        if user:
            session['restaurant_id'] = user[0]
            return redirect('/dashboard')
    return '<h2>Login</h2><form method="POST"><input name="email" placeholder="email"><br><input name="password" type="password" placeholder="password"><br><button>Login</button></form>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)