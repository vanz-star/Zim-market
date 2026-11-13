from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zimmarket-2026-pro'
# Use Render DB if exists, else local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///zim.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50), default='All')
    image = db.Column(db.String(300), default='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500')
    restaurant = db.Column(db.String(100), default='ZimMarket Kitchen')

with app.app_context():
    db.create_all()

# --- PRO TEMPLATE ---
PRO_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZimMarket - Food Delivery Zimbabwe</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap" rel="stylesheet">
</head>
<body>
<style>
*{font-family:'Inter',system-ui}
body{margin:0;background:#f7f7f7}
.nav{display:flex;justify-content:space-between;padding:14px 24px;background:#fff;align-items:center;position:sticky;top:0;z-index:10;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.logo{font-weight:900;font-size:24px} .logo span{color:#06c167}
.search-bar{background:#f0f0f0;padding:10px 16px;border-radius:24px;display:flex;gap:8px;min-width:280px} .search-bar input{border:0;background:transparent;outline:none;width:100%}
.btns{display:flex;gap:10px} .btn{padding:10px 20px;border-radius:24px;text-decoration:none;font-weight:600;font-size:14px} .btn-light{background:#eee;color:#000} .btn-dark{background:#000;color:#fff}
.hero{background:#fff;display:flex;padding:40px;gap:40px;align-items:center}
.hero-text{flex:1} .hero-text h1{font-size:52px;line-height:0.95;margin:0;font-weight:900;letter-spacing:-2px} .hero-text h1 span{color:#666;font-weight:400} .hero-text p{color:#666;margin:16px 0;font-size:16px}
.hero-input{display:flex;background:#f0f0f0;border-radius:12px;padding:6px;margin:20px 0;max-width:480px} .hero-input input{flex:1;border:0;background:transparent;padding:14px;outline:none;font-size:16px} .hero-input button{background:#000;color:#fff;border:0;padding:14px 24px;border-radius:10px;font-weight:600;cursor:pointer}
.hero-img{flex:1} .hero-img img{width:100%;border-radius:20px;object-fit:cover;max-height:400px}
.cats{display:flex;gap:10px;padding:16px 24px;overflow:auto;background:#fff;border-top:1px solid #eee;border-bottom:1px solid #eee;position:sticky;top:64px;z-index:9}
.cat{background:#f0f0f0;padding:10px 16px;border-radius:24px;white-space:nowrap;cursor:pointer;font-size:14px;font-weight:500} .cat.active{background:#000;color:#fff} .cat:hover{background:#e0e0e0}
.wrap{padding:24px} .section-title{font-size:22px;font-weight:900;margin:10px 0 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);transition:0.2s} .card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.12)}
.card img{width:100%;height:180px;object-fit:cover} .card-body{padding:14px}
.card-title{font-weight:700;margin:0} .card-sub{color:#666;font-size:13px;margin:4px 0}
.card-foot{display:flex;justify-content:space-between;align-items:center;margin-top:10px} .price{font-weight:900} .add-btn{background:#06c167;color:#fff;border:0;padding:8px 14px;border-radius:20px;font-weight:600;cursor:pointer}
.badges{display:flex;gap:6px;margin:8px 0} .badge{font-size:11px;background:#e8f8f0;color:#06c167;padding:4px 8px;border-radius:12px;font-weight:600}
.pay-bar{background:#fff;padding:16px 24px;display:flex;gap:20px;align-items:center;border-top:1px solid #eee} .pay-bar img{height:24px}
.footer{text-align:center;padding:40px;color:#888;font-size:13px;line-height:1.6}
@media(max-width:800px){.hero{flex-direction:column;padding:24px} .hero-text h1{font-size:36px} .search-bar{display:none}}
</style>

<div class="nav">
  <div class="logo">Zim<span>Market</span></div>
  <div class="search-bar">🔍 <form method="GET" style="display:flex;flex:1"><input name="q" value="{{q}}" placeholder="Food, groceries, drinks, etc."></form></div>
  <div class="btns"><a href="/login" class="btn btn-light">Log in</a><a href="/admin" class="btn btn-dark">Admin</a></div>
</div>

<div class="hero">
  <div class="hero-text">
    <h1>Food delivery <br>and more <span>— Zimbabwe</span></h1>
    <p>Groceries, alcohol and convenience products in Harare. Order with EcoCash, ZiG, USD.</p>
    <div class="hero-input"><input placeholder="Enter delivery address"><button>Find Food</button></div>
    <div class="badges"><span class="badge">⚡ 30 min delivery</span><span class="badge">💳 EcoCash</span><span class="badge">📍 Harare</span></div>
  </div>
  <div class="hero-img"><img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800"></div>
</div>

<div class="cats">
  <a href="/?cat=All" style="text-decoration:none"><div class="cat {{'active' if cat=='All' else ''}}">All</div></a>
  <a href="/?cat=Burgers" style="text-decoration:none"><div class="cat {{'active' if cat=='Burgers' else ''}}">🍔 Burgers</div></a>
  <a href="/?cat=Chicken" style="text-decoration:none"><div class="cat {{'active' if cat=='Chicken' else ''}}">🍗 Chicken</div></a>
  <a href="/?cat=Local" style="text-decoration:none"><div class="cat {{'active' if cat=='Local' else ''}}">🥘 Sadza & Local</div></a>
  <a href="/?cat=Drinks" style="text-decoration:none"><div class="cat {{'active' if cat=='Drinks' else ''}}">🍹 Drinks</div></a>
  <a href="/?cat=Grocery" style="text-decoration:none"><div class="cat {{'active' if cat=='Grocery' else ''}}">🛒 Grocery</div></a>
</div>

<div class="wrap">
  <div class="section-title">{{cat}} near you • {{dishes|length}} stores</div>
  <div class="grid">
    {% for d in dishes %}
    <div class="card">
      <img src="{{d.image}}">
      <div class="card-body">
        <p class="card-title">{{d.name}}</p>
        <p class="card-sub">{{d.restaurant}} • 25-35 min • ★ 4.8</p>
        <div class="badges"><span class="badge">Free delivery</span></div>
        <div class="card-foot">
          <span class="price">${{d.price}}</span>
          <button class="add-btn">Add to cart</button>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
  {% if not dishes %}
  <div style="text-align:center;padding:60px;background:#fff;border-radius:16px;margin-top:20px">
    <h3>No dishes in {{cat}} yet</h3>
    <p>Go to <a href="/admin">/admin</a> to add your first dish - Sadza, Burgers, etc.</p>
    <a href="/admin/add-sample" style="background:#06c167;color:#fff;padding:12px 20px;border-radius:24px;text-decoration:none;display:inline-block;margin-top:10px">Add Sample Dishes</a>
  </div>
  {% endif %}
</div>

<div class="pay-bar">
  <span style="font-weight:700;font-size:13px">PAY WITH:</span>
  <span style="background:#1e8e3e;color:#fff;padding:4px 10px;border-radius:6px;font-weight:700;font-size:12px">EcoCash</span>
  <span style="background:#ffd400;padding:4px 10px;border-radius:6px;font-weight:700;font-size:12px">ZiG</span>
  <span style="background:#000;color:#fff;padding:4px 10px;border-radius:6px;font-weight:700;font-size:12px">USD • VISA</span>
</div>

<div class="footer">
  © 2026 ZimMarket • Made with ❤️ by Evex Tech • Harare, Zimbabwe zw<br>
  Delivering in: Borrowdale • Avondale • CBD • Mount Pleasant • Chitungwiza<br>
  <a href="/admin" style="color:#888">Admin Dashboard</a> • Powered by Render
</div>
</body>
</html>
"""

@app.route('/')
def home():
    q = request.args.get('q', '')
    cat = request.args.get('cat', 'All')
    query = Dish.query
    if q:
        query = query.filter(Dish.name.ilike(f'%{q}%'))
    if cat != 'All':
        query = query.filter_by(category=cat)
    dishes = query.all()
    return render_template_string(PRO_PAGE, dishes=dishes, q=q, cat=cat)

@app.route('/admin')
def admin():
    dishes = Dish.query.all()
    html = "<h2>ZimMarket Admin</h2><a href='/'>Home</a> | <a href='/admin/add-sample'>Add Sample Dishes</a><hr>"
    for d in dishes:
        html += f"{d.name} - ${d.price} - {d.category} <a href='/admin/delete/{d.id}'>Delete</a><br>"
    html += """
    <hr><h3>Add Dish</h3>
    <form method='POST' action='/admin/add'>
    Name: <input name='name'><br>
    Price: <input name='price' type='number' step='0.01'><br>
    Category: <select name='category'><option>All</option><option>Burgers</option><option>Chicken</option><option>Local</option><option>Drinks</option><option>Grocery</option></select><br>
    Image URL: <input name='image' style='width:300px'><br>
    Restaurant: <input name='restaurant'><br>
    <button>Add</button></form>
    """
    return html

@app.route('/admin/add', methods=['POST'])
def add_dish():
    d = Dish(
        name=request.form['name'],
        price=float(request.form['price']),
        category=request.form['category'],
        image=request.form['image'] or 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500',
        restaurant=request.form['restaurant'] or 'ZimMarket Kitchen'
    )
    db.session.add(d)
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/delete/<int:id>')
def delete_dish(id):
    d = Dish.query.get(id)
    if d:
        db.session.delete(d)
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/add-sample')
def add_sample():
    if Dish.query.count() == 0:
        samples = [
            Dish(name='Double Cheese Burger', price=5.5, category='Burgers', restaurant='Chicken Inn', image='https://images.unsplash.com/photo-1568909344668-6f14a07b56a0?w=500'),
            Dish(name='Sadza & Chicken Stew', price=4.0, category='Local', restaurant='Mama\'s Kitchen', image='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500'),
            Dish(name='Fried Chicken Bucket', price=12.0, category='Chicken', restaurant='Chicken Slice', image='https://images.unsplash.com/photo-1626645738196-c2a046020eb6?w=500'),
            Dish(name='Coca-Cola 2L', price=2.5, category='Drinks', restaurant='ZimMart Grocery', image='https://images.unsplash.com/photo-1554866585-cd94860890b7?w=500'),
            Dish(name='Mazoe Orange 2L', price=3.0, category='Drinks', restaurant='ZimMart Grocery', image='https://images.unsplash.com/photo-1624552184280-9e9631bbeee9?w=500'),
            Dish(name='Tomato & Onion Bundle', price=3.5, category='Grocery', restaurant='Fresh Market', image='https://images.unsplash.com/photo-1542838132-92c53300491e?w=500'),
        ]
        db.session.add_all(samples)
        db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

