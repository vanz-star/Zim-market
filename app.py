from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zimmarket-final-2026-pro-evex'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///zim.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), default='All')
    image = db.Column(db.String(500), default='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500')
    restaurant = db.Column(db.String(100), default='ZimMarket Kitchen')
    is_available = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dish_name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    # Create admin if not exists
    if not User.query.filter_by(email='admin@zimmarket.co.zw').first():
        admin = User(email='admin@zimmarket.co.zw', phone='0770000000', password_hash=generate_password_hash('Admin123!'), is_admin=True)
        db.session.add(admin)
        db.session.commit()

# --- TEMPLATES ---
BASE_CSS = """
<style>
*{font-family:Inter,system-ui;margin:0} body{background:#f7f7f7}
.nav{display:flex;justify-content:space-between;padding:14px 24px;background:#fff;align-items:center;position:sticky;top:0;z-index:20;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.logo{font-weight:900;font-size:24px;text-decoration:none;color:#000} .logo span{color:#06c167}
.btns{display:flex;gap:10px;align-items:center} .btn{padding:10px 20px;border-radius:24px;text-decoration:none;font-weight:600;font-size:14px;display:inline-block} .btn-light{background:#eee;color:#000} .btn-dark{background:#000;color:#fff} .btn-green{background:#06c167;color:#fff}
.wrap{max-width:1100px;margin:0 auto;padding:24px}
.card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:16px}
input,select{width:100%;padding:12px 14px;border:1px solid #ddd;border-radius:10px;margin:8px 0;font-size:15px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.dish-card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.dish-card img{width:100%;height:180px;object-fit:cover} .dish-body{padding:14px}
.admin-grid{display:grid;grid-template-columns:250px 1fr;gap:20px} .sidebar{background:#000;color:#fff;border-radius:16px;padding:20px;height:fit-content;position:sticky;top:80px} .sidebar a{display:block;color:#aaa;text-decoration:none;padding:10px 0} .sidebar a.active,.sidebar a:hover{color:#fff}
.stat{display:inline-block;background:#fff;padding:16px 24px;border-radius:12px;margin-right:12px;min-width:140px} .stat b{font-size:24px;display:block}
</style>
"""

HOME_HTML = BASE_CSS + """
<div class="nav">
  <a href="/" class="logo">Zim<span>Market</span></a>
  <div class="btns">
    {% if current_user.is_authenticated %}
      <span style="font-size:14px">Hi, {{current_user.email.split('@')[0]}} {% if current_user.is_admin %} (Admin) {% endif %}</span>
      {% if current_user.is_admin %}<a href="/admin" class="btn btn-green">Admin Portal</a>{% endif %}
      <a href="/logout" class="btn btn-light">Logout</a>
    {% else %}
      <a href="/login" class="btn btn-light">Log in</a>
      <a href="/signup" class="btn btn-dark">Sign up</a>
    {% endif %}
  </div>
</div>
<div style="background:#fff;padding:40px;display:flex;gap:40px;align-items:center;flex-wrap:wrap">
  <div style="flex:1;min-width:300px"><h1 style="font-size:52px;font-weight:900;line-height:.9">Food delivery<br>and more <span style="color:#666;font-weight:400">— Zimbabwe</span></h1>
  <p style="color:#666;margin:16px 0">Groceries, alcohol and convenience in Harare. Order with EcoCash, ZiG, USD.</p>
  <div style="display:flex;background:#f0f0f0;border-radius:12px;padding:6px;max-width:480px"><input placeholder="Enter delivery address" style="border:0;background:transparent;margin:0"><button style="background:#000;color:#fff;border:0;padding:12px 20px;border-radius:10px;font-weight:600">Find Food</button></div></div>
  <div style="flex:1;min-width:300px"><img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800" style="width:100%;border-radius:20px"></div>
</div>
<div style="background:#fff;padding:12px 24px;display:flex;gap:10px;overflow:auto;border-top:1px solid #eee">
  {% for c in ['All','Burgers','Chicken','Local','Drinks','Grocery'] %}
  <a href="/?cat={{c}}" style="text-decoration:none"><div style="padding:10px 16px;border-radius:24px;background:{{'#000' if cat==c else '#f0f0f0'}};color:{{'#fff' if cat==c else '#000'}};white-space:nowrap;font-size:14px;font-weight:500">{{c}}</div></a>
  {% endfor %}
</div>
<div class="wrap">
  <h3 style="margin:10px 0 16px">{{cat}} • {{dishes|length}} items</h3>
  <div class="grid">
  {% for d in dishes %}
    <div class="dish-card"><img src="{{d.image}}"><div class="dish-body"><b>{{d.name}}</b><p style="color:#666;font-size:13px">{{d.restaurant}} • 30 min • ★ 4.8</p><div style="display:flex;justify-content:space-between;margin-top:10px"><b>${{d.price}}</b><form method="POST" action="/order/{{d.id}}"><button class="btn btn-green" style="padding:6px 12px;font-size:13px">Add to cart</button></form></div></div></div>
  {% endfor %}
  </div>
</div>
"""

AUTH_HTML = BASE_CSS + """
<div class="nav"><a href="/" class="logo">Zim<span>Market</span></a></div>
<div class="wrap" style="max-width:420px">
<div class="card">
<h2 style="font-weight:900;margin-bottom:6px">{{title}}</h2>
<p style="color:#666;font-size:14px;margin-bottom:16px">{{subtitle}}</p>
{% if error %}<div style="background:#ffe0e0;color:#b00;padding:10px;border-radius:8px;margin-bottom:10px;font-size:14px">{{error}}</div>{% endif %}
<form method="POST">
{% if is_signup %}
<input name="email" type="email" placeholder="Email address" required>
<input name="phone" placeholder="Phone number e.g. 0771234567" required>
{% else %}
<input name="email" type="email" placeholder="Email address" required>
{% endif %}
<input name="password" type="password" placeholder="Password" required>
<button class="btn btn-dark" style="width:100%;margin-top:12px;padding:14px">{{btn}}</button>
</form>
<p style="text-align:center;margin-top:16px;font-size:14px">
{% if is_signup %}Already have account? <a href="/login">Log in</a>{% else %}No account? <a href="/signup">Sign up</a>{% endif %} | <a href="/">Home</a>
</p>
{% if is_signup %}<p style="text-align:center;margin-top:20px;background:#f0f0f0;padding:10px;border-radius:10px;font-size:12px">Admin login: admin@zimmarket.co.zw / Admin123!</p>{% endif %}
</div></div>
"""

ADMIN_HTML = BASE_CSS + """
<div class="nav"><a href="/" class="logo">Zim<span>Market</span> Admin</a><div class="btns"><span>{{current_user.email}}</span><a href="/" class="btn btn-light">View Site</a><a href="/logout" class="btn btn-dark">Logout</a></div></div>
<div class="wrap"><div class="admin-grid">
<div class="sidebar">
<h3 style="margin-bottom:16px">Control Panel</h3>
<a href="/admin" class="{{'active' if page=='dash' else ''}}">📊 Dashboard</a>
<a href="/admin?tab=users" class="{{'active' if tab=='users' else ''}}">👥 Users ({{users|length}})</a>
<a href="/admin?tab=dishes" class="{{'active' if tab=='dishes' else ''}}">🍔 Dishes ({{dishes|length}})</a>
<a href="/admin?tab=orders" class="{{'active' if tab=='orders' else ''}}">📦 Orders ({{orders|length}})</a>
<a href="/admin/add-sample" style="margin-top:20px;color:#06c167">+ Add Sample Data</a>
</div>
<div>
{% if page=='dash' %}
<h2>Dashboard</h2><br>
<div class="stat"><b>{{users|length}}</b> Total Users</div>
<div class="stat"><b>{{dishes|length}}</b> Dishes</div>
<div class="stat"><b>{{orders|length}}</b> Orders</div>
<div class="stat"><b>${{ "%.2f"|format(total) }}</b> Revenue</div>
<div class="card" style="margin-top:20px"><h3>Recent Orders</h3>
{% for o in orders[:10] %}<div style="padding:8px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between"><span>#{{o.id}} {{o.dish_name}} - ${{o.amount}} - {{o.status}}</span><span style="font-size:12px;color:#888">{{o.created_at.strftime('%d/%m %H:%M')}}</span></div>{% endfor %}
</div>
{% endif %}

{% if tab=='users' %}
<h2>All Users - Full Control</h2><div class="card">
<table style="width:100%;font-size:14px"><tr style="text-align:left;color:#888"><th>Email</th><th>Phone</th><th>Admin</th><th>Date</th><th>Action</th></tr>
{% for u in users %}<tr><td>{{u.email}}</td><td>{{u.phone}}</td><td>{{'Yes' if u.is_admin else 'No'}}</td><td>{{u.created_at.strftime('%d/%m')}}</td><td><a href="/admin/make-admin/{{u.id}}">Make Admin</a> | <a href="/admin/delete-user/{{u.id}}" style="color:red" onclick="return confirm('Delete?')">Delete</a></td></tr>{% endfor %}
</table></div>
{% endif %}

{% if tab=='dishes' %}
<h2>Manage Dishes</h2>
<div class="card"><h3>Add New Dish</h3>
<form method="POST" action="/admin/add"><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
<input name="name" placeholder="Name e.g. Sadza & Beef" required><input name="price" type="number" step="0.01" placeholder="Price e.g. 5.5" required>
<input name="category" placeholder="Category: Burgers, Chicken, Local, Drinks, Grocery" required><input name="restaurant" placeholder="Restaurant name" required>
</div><input name="image" placeholder="Image URL (or leave empty)"><button class="btn btn-green" style="margin-top:10px">Add Dish</button></form></div>
<div class="grid" style="margin-top:16px">
{% for d in dishes %}<div class="dish-card"><img src="{{d.image}}"><div class="dish-body"><b>{{d.name}}</b><p style="font-size:13px;color:#666">${{d.price}} - {{d.category}} - {{d.restaurant}}</p><a href="/admin/delete-dish/{{d.id}}" style="color:red;font-size:13px">Delete</a> • {{'Available' if d.is_available else 'Hidden'}}</div></div>{% endfor %}
</div>
{% endif %}

{% if tab=='orders' %}
<h2>All Orders - Full Control</h2><div class="card">
{% for o in orders %}<div style="padding:12px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center"><div><b>#{{o.id}}</b> {{o.dish_name}} - ${{o.amount}}<br><span style="font-size:12px;color:#666">User ID {{o.user_id}} - {{o.created_at.strftime('%d/%m %Y %H:%M')}}</span></div><div><span style="background:#e8f8f0;padding:4px 10px;border-radius:12px;font-size:12px">{{o.status}}</span> <a href="/admin/order-status/{{o.id}}" style="margin-left:10px;font-size:13px">Next Status</a></div></div>{% endfor %}
</div>
{% endif %}
</div></div></div>
"""

@app.route('/')
def home():
    cat = request.args.get('cat','All')
    q = Dish.query
    if cat!='All': q=q.filter_by(category=cat)
    dishes = q.all()
    return render_template_string(HOME_HTML, dishes=dishes, cat=cat)

@app.route('/signup', methods=['GET','POST'])
def signup():
    error=None
    if request.method=='POST':
        email=request.form['email'].lower().strip()
        phone=request.form['phone'].strip()
        password=request.form['password']
        if User.query.filter_by(email=email).first():
            error="Email already exists!"
        elif len(password)<6:
            error="Password must be 6+ characters"
        elif not phone:
            error="Phone number required"
        else:
            user=User(email=email, phone=phone, password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit()
            login_user(user)
            return redirect('/')
    return render_template_string(AUTH_HTML, title="Create account", subtitle="Sign up with email, phone and password", btn="Sign up", is_signup=True, error=error)

@app.route('/login', methods=['GET','POST'])
def login():
    error=None
    if request.method=='POST':
        email=request.form['email'].lower().strip()
        password=request.form['password']
        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.is_admin: return redirect('/admin')
            return redirect('/')
        error="Invalid email or password"
    return render_template_string(AUTH_HTML, title="Log in", subtitle="Welcome back to ZimMarket", btn="Log in", is_signup=False, error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/order/<int:dish_id>', methods=['POST'])
@login_required
def make_order(dish_id):
    dish=Dish.query.get(dish_id)
    if dish:
        order=Order(user_id=current_user.id, dish_name=dish.name, amount=dish.price)
        db.session.add(order); db.session.commit()
    return redirect('/?ordered=1')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin: return "Access Denied - Admin only",403
    tab=request.args.get('tab','')
    page='dash' if not tab else ''
    users=User.query.order_by(User.created_at.desc()).all()
    dishes=Dish.query.all()
    orders=Order.query.order_by(Order.created_at.desc()).all()
    total=sum([o.amount for o in orders])
    return render_template_string(ADMIN_HTML, users=users, dishes=dishes, orders=orders, total=total, tab=tab, page=page)

@app.route('/admin/add', methods=['POST'])
@login_required
def admin_add():
    if not current_user.is_admin: return "Denied",403
    d=Dish(name=request.form['name'], price=float(request.form['price']), category=request.form['category'], restaurant=request.form['restaurant'], image=request.form['image'] or 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500')
    db.session.add(d); db.session.commit()
    return redirect('/admin?tab=dishes')

@app.route('/admin/delete-dish/<int:id>')
@login_required
def admin_del_dish(id):
    if not current_user.is_admin: return "Denied",403
    d=Dish.query.get(id); 
    if d: db.session.delete(d); db.session.commit()
    return redirect('/admin?tab=dishes')

@app.route('/admin/delete-user/<int:id>')
@login_required
def admin_del_user(id):
    if not current_user.is_admin: return "Denied",403
    if id==current_user.id: return "Cannot delete yourself"
    u=User.query.get(id)
    if u: db.session.delete(u); db.session.commit()
    return redirect('/admin?tab=users')

@app.route('/admin/make-admin/<int:id>')
@login_required
def admin_make(id):
    if not current_user.is_admin: return "Denied",403
    u=User.query.get(id); 
    if u: u.is_admin=not u.is_admin; db.session.commit()
    return redirect('/admin?tab=users')

@app.route('/admin/order-status/<int:id>')
@login_required
def admin_order_status(id):
    if not current_user.is_admin: return "Denied",403
    o=Order.query.get(id)
    if o:
        o.status = {'Pending':'Preparing','Preparing':'Out for delivery','Out for delivery':'Delivered','Delivered':'Pending'}[o.status]
        db.session.commit()
    return redirect('/admin?tab=orders')

@app.route('/admin/add-sample')
@login_required
def admin_sample():
    if not current_user.is_admin: return "Denied",403
    if Dish.query.count()==0:
        samples=[
            Dish(name='Double Cheese Burger',price=5.5,category='Burgers',restaurant='Chicken Inn',image='https://images.unsplash.com/photo-1568909344668-6f14a07b56a0?w=500'),
            Dish(name='Sadza & Chicken Stew',price=4.0,category='Local',restaurant="Mama's Kitchen",image='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500'),
            Dish(name='Fried Chicken Bucket',price=12.0,category='Chicken',restaurant='Chicken Slice',image='https://images.unsplash.com/photo-1626645738196-c2a046020eb6?w=500'),
            Dish(name='Coca-Cola 2L',price=2.5,category='Drinks',restaurant='ZimMart',image='https://images.unsplash.com/photo-1554866585-cd94860890b7?w=500'),
            Dish(name='Mazoe Orange',price=3.0,category='Drinks',restaurant='ZimMart',image='https://images.unsplash.com/photo-1624552184280-9e9631bbeee9?w=500'),
        ]
        db.session.add_all(samples); db.session.commit()
    return redirect('/admin?tab=dishes')

if __name__=="__main__":
    app.run(host='0.0.0.0',port=10000)