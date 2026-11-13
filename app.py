from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zim-restaurant-portal-final'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///zim.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500), default='Best food in Harare')
    location = db.Column(db.String(200), default='Harare, Zimbabwe')
    phone = db.Column(db.String(20), default='0770000000')
    image = db.Column(db.String(500), default='https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500')
    rating = db.Column(db.Float, default=4.8)
    delivery_time = db.Column(db.String(20), default='30-45 min')
    is_open = db.Column(db.Boolean, default=True)
    ecocash_number = db.Column(db.String(100), default='To be added after agreement')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(500), default='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.relationship('Restaurant', backref='dishes')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    dish_name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@zimmarket.co.zw').first():
        db.session.add(User(email='admin@zimmarket.co.zw', phone='0770000000', password_hash=generate_password_hash('Admin123!'), is_admin=True))
        db.session.commit()
    if Restaurant.query.count()==0:
        rests=[
            Restaurant(name='Chicken Inn', description='Zimbabwe favourite chicken & burgers', location='Samora Machel Ave, Harare CBD', phone='0291234567', image='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600', rating=4.8, delivery_time='20-30 min'),
            Restaurant(name="Mama's Traditional Kitchen", description='Authentic sadza, muriwo, beef, chicken', location='Mbare, Harare', phone='0771234567', image='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600', rating=4.9, delivery_time='25-35 min'),
            Restaurant(name='Chicken Slice', description='Flame grilled chicken specialists', location='Angwa St, Harare', phone='0719876543', image='https://images.unsplash.com/photo-1626645738196-c2a046020eb6?w=600', rating=4.7, delivery_time='15-25 min'),
            Restaurant(name='Pizza Inn', description='Best pizza in Zim - fresh & hot', location='Borrowdale, Harare', phone='0778889999', image='https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600', rating=4.8, delivery_time='30-40 min'),
        ]
        db.session.add_all(rests); db.session.commit()
        # Add dishes to each
        r1=Restaurant.query.filter_by(name='Chicken Inn').first()
        r2=Restaurant.query.filter_by(name="Mama's Traditional Kitchen").first()
        r3=Restaurant.query.filter_by(name='Chicken Slice').first()
        r4=Restaurant.query.filter_by(name='Pizza Inn').first()
        dishes=[
            Dish(name='2 Piece Chicken & Chips',price=6.5,restaurant_id=r1.id,image='https://images.unsplash.com/photo-1626645738196-c2a046020eb6?w=500'),
            Dish(name='Double Cheese Burger',price=5.5,restaurant_id=r1.id,image='https://images.unsplash.com/photo-1568909344668-6f14a07b56a0?w=500'),
            Dish(name='Sadza & Road Runner',price=4.5,restaurant_id=r2.id),
            Dish(name='Sadza & Beef Stew',price=5.0,restaurant_id=r2.id),
            Dish(name='Full Chicken Braai',price=14.0,restaurant_id=r3.id,image='https://images.unsplash.com/photo-1615937657715-bc7b4b7962c1?w=500'),
            Dish(name='Chicken Burger',price=4.5,restaurant_id=r3.id),
            Dish(name='Margherita Pizza Large',price=12.0,restaurant_id=r4.id,image='https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500'),
            Dish(name='Pepperoni Pizza',price=13.5,restaurant_id=r4.id),
        ]
        db.session.add_all(dishes); db.session.commit()

CSS="""
<style>
*{font-family:Inter,system-ui;margin:0} body{background:#f7f7f7}
.nav{display:flex;justify-content:space-between;padding:14px 24px;background:#fff;align-items:center;position:sticky;top:0;z-index:20;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.logo{font-weight:900;font-size:22px;text-decoration:none;color:#000} .logo span{color:#06c167}
.btn{padding:10px 18px;border-radius:24px;text-decoration:none;font-weight:600;font-size:14px;display:inline-block;border:0;cursor:pointer} .btn-light{background:#eee;color:#000} .btn-dark{background:#000;color:#fff} .btn-green{background:#06c167;color:#fff}
.wrap{max-width:1100px;margin:0 auto;padding:20px}
.rest-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}
.rest-card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06);cursor:pointer;transition:.2s} .rest-card:hover{transform:translateY(-4px)}
.rest-card img{width:100%;height:200px;object-fit:cover} .rest-body{padding:16px}
.rest-top{display:flex;justify-content:space-between;align-items:center}
.badge{background:#f0f0f0;padding:4px 10px;border-radius:12px;font-size:12px}
.hero{display:flex;gap:30px;padding:24px;background:#fff;border-radius:20px;margin-bottom:20px}
.hero img{width:340px;height:220px;border-radius:16px;object-fit:cover}
.menu-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
.menu-card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.menu-card img{width:100%;height:160px;object-fit:cover}
input{width:100%;padding:12px;border:1px solid #ddd;border-radius:10px;margin:6px 0}
</style>
"""

@app.route('/')
def home():
    restaurants=Restaurant.query.filter_by(is_open=True).all()
    selected=request.args.get('restaurant')
    return render_template_string(CSS+"""
<div class="nav"><a href="/" class="logo">Zim<span>Market</span></a>
<div style="display:flex;gap:10px;align-items:center">
{% if current_user.is_authenticated %}<span style="font-size:13px">Hi, {{current_user.email.split('@')[0]}}</span>{% if current_user.is_admin %}<a href="/admin" class="btn btn-green" style="padding:6px 12px">Admin</a>{% endif %}<a href="/logout" class="btn btn-light">Logout</a>
{% else %}<a href="/login" class="btn btn-light">Log in</a><a href="/signup" class="btn btn-dark">Sign up</a>{% endif %}
</div></div>
<div style="background:#fff;padding:30px 24px"><h1 style="font-size:42px;font-weight:900">Restaurants in Harare</h1><p style="color:#666;margin-top:6px">Click any restaurant to see its full menu, location & order directly from that restaurant</p></div>
<div style="background:#fff;padding:12px 24px;display:flex;gap:10px;overflow:auto;border-top:1px solid #eee;border-bottom:1px solid #eee;position:sticky;top:58px;z-index:10">
<a href="/"><div class="btn {{'btn-dark' if not selected else 'btn-light'}}" style="white-space:nowrap">All Restaurants</div></a>
{% for r in restaurants %}<a href="/restaurant/{{r.id}}"><div class="btn btn-light" style="white-space:nowrap">{{r.name}}</div></a>{% endfor %}
</div>
<div class="wrap">
<div class="rest-grid">
{% for r in restaurants %}
<a href="/restaurant/{{r.id}}" style="text-decoration:none;color:#000">
<div class="rest-card"><img src="{{r.image}}"><div class="rest-body">
<div class="rest-top"><b style="font-size:18px">{{r.name}}</b><span class="badge">★ {{r.rating}}</span></div>
<p style="color:#666;font-size:14px;margin:6px 0">{{r.description}}</p>
<p style="font-size:13px;color:#888">{{r.location}} • {{r.delivery_time}} • {{r.dishes|length}} dishes</p>
</div></div></a>
{% endfor %}
</div></div>
""", restaurants=restaurants, selected=selected)

@app.route('/restaurant/<int:id>')
def restaurant_portal(id):
    r=Restaurant.query.get_or_404(id)
    return render_template_string(CSS+"""
<div class="nav"><a href="/" class="logo">Zim<span>Market</span></a><a href="/" class="btn btn-light">← All Restaurants</a></div>
<div class="wrap">
<div class="hero">
<img src="{{r.image}}">
<div style="flex:1"><h1 style="font-size:36px;font-weight:900">{{r.name}}</h1>
<p style="color:#666;margin:8px 0">{{r.description}}</p>
<p style="font-size:14px">📍 {{r.location}}<br>📞 {{r.phone}}<br>⭐ {{r.rating}} • {{r.delivery_time}} • {% if r.is_open %} <span style="color:green">● Open now</span> {% else %} Closed {% endif %}</p>
<div style="margin-top:14px;background:#f7f7f7;padding:12px;border-radius:10px;font-size:13px"><b>Payment to this restaurant:</b><br>EcoCash / ZiG / USD: {{r.ecocash_number}}<br><i>Payment goes directly to {{r.name}} owner - after agreement</i></div>
</div></div>
<h2 style="margin:10px 0">{{r.dishes|length}} Menu Items</h2>
<div class="menu-grid">
{% for d in r.dishes %}
<div class="menu-card"><img src="{{d.image}}"><div style="padding:14px">
<b>{{d.name}}</b><p style="color:#666;font-size:13px;margin:4px 0">${{d.price}}</p>
{% if current_user.is_authenticated %}
<form method="POST" action="/order/{{d.id}}"><button class="btn btn-green" style="width:100%;margin-top:6px">Order now - ${{d.price}}</button></form>
{% else %}
<a href="/login" class="btn btn-dark" style="width:100%;margin-top:6px;text-align:center">Login to Order</a>
{% endif %}
</div></div>
{% endfor %}
</div>
</div>
""", r=r)

@app.route('/signup', methods=['GET','POST'])
def signup():
    err=None
    if request.method=='POST':
        e=request.form['email'].lower().strip(); p=request.form['phone']; pw=request.form['password']
        if User.query.filter_by(email=e).first(): err="Email exists"
        else:
            u=User(email=e, phone=p, password_hash=generate_password_hash(pw)); db.session.add(u); db.session.commit(); login_user(u); return redirect('/')
    return render_template_string(CSS+"""<div class="nav"><a href="/" class="logo">Zim<span>Market</span></a></div><div class="wrap" style="max-width:420px"><div style="background:#fff;padding:24px;border-radius:16px"><h2>Create Account</h2><p style="color:#666;font-size:14px">Email, phone, password required</p>{% if err %}<div style="background:#ffe0e0;padding:8px;border-radius:6px;color:#900;margin:10px 0">{{err}}</div>{% endif %}<form method="POST"><input name="email" type="email" placeholder="Email" required><input name="phone" placeholder="Phone number e.g. 0771234567" required><input name="password" type="password" placeholder="Password" required><button class="btn btn-dark" style="width:100%;padding:14px;margin-top:10px">Sign up</button></form><p style="text-align:center;margin-top:12px;font-size:14px"><a href="/login">Already have account? Login</a></p><p style="text-align:center;margin-top:10px;font-size:11px;background:#f0f0f0;padding:8px;border-radius:8px">Admin: admin@zimmarket.co.zw / Admin123!</p></div></div>""", err=err)

@app.route('/login', methods=['GET','POST'])
def login():
    err=None
    if request.method=='POST':
        e=request.form['email'].lower().strip(); pw=request.form['password']
        u=User.query.filter_by(email=e).first()
        if u and check_password_hash(u.password_hash, pw): login_user(u); return redirect('/admin' if u.is_admin else '/')
        err="Invalid login"
    return render_template_string(CSS+"""<div class="nav"><a href="/" class="logo">Zim<span>Market</span></a></div><div class="wrap" style="max-width:420px"><div style="background:#fff;padding:24px;border-radius:16px"><h2>Login</h2>{% if err %}<div style="background:#ffe0e0;padding:8px;border-radius:6px;color:#900;margin:10px 0">{{err}}</div>{% endif %}<form method="POST"><input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Password" required><button class="btn btn-dark" style="width:100%;padding:14px;margin-top:10px">Log in</button></form><p style="text-align:center;margin-top:12px;font-size:14px"><a href="/signup">No account? Sign up</a></p></div></div>""", err=err)

@app.route('/logout')
def logout(): logout_user(); return redirect('/')
@app.route('/order/<int:dish_id>', methods=['POST'])
@login_required
def order(dish_id):
    d=Dish.query.get(dish_id)
    if d: 
        o=Order(user_id=current_user.id, restaurant_id=d.restaurant_id, dish_name=d.name, amount=d.price)
        db.session.add(o); db.session.commit()
    return redirect(f'/restaurant/{d.restaurant_id}?ordered=1')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin: return "Admin only",403
    tab=request.args.get('tab','dash')
    users=User.query.all(); rests=Restaurant.query.all(); dishes=Dish.query.all(); orders=Order.query.order_by(Order.created_at.desc()).all()
    return render_template_string(CSS+"""
<div class="nav"><a href="/" class="logo">Zim<span>Market</span> Admin</a><div style="display:flex;gap:10px"><a href="/" class="btn btn-light">View Site</a><a href="/logout" class="btn btn-dark">Logout</a></div></div>
<div class="wrap"><h2>Admin Control Panel - Full System Control</h2><br>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px">
<a href="/admin?tab=dash" class="btn {{'btn-dark' if tab=='dash' else 'btn-light'}}">Dashboard</a>
<a href="/admin?tab=restaurants" class="btn {{'btn-dark' if tab=='restaurants' else 'btn-light'}}">Restaurants ({{rests|length}})</a>
<a href="/admin?tab=dishes" class="btn {{'btn-dark' if tab=='dishes' else 'btn-light'}}">Dishes ({{dishes|length}})</a>
<a href="/admin?tab=users" class="btn {{'btn-dark' if tab=='users' else 'btn-light'}}">Users ({{users|length}})</a>
<a href="/admin?tab=orders" class="btn {{'btn-dark' if tab=='orders' else 'btn-light'}}">Orders ({{orders|length}})</a>
</div>
{% if tab=='dash' %}
<div style="display:flex;gap:12px;flex-wrap:wrap"><div style="background:#fff;padding:20px;border-radius:12px"><b style="font-size:24px">{{rests|length}}</b><br>Restaurants</div><div style="background:#fff;padding:20px;border-radius:12px"><b style="font-size:24px">{{users|length}}</b><br>Users</div><div style="background:#fff;padding:20px;border-radius:12px"><b style="font-size:24px">{{dishes|length}}</b><br>Dishes</div><div style="background:#fff;padding:20px;border-radius:12px"><b style="font-size:24px">{{orders|length}}</b><br>Orders</div></div>
<div style="background:#fff;padding:20px;border-radius:16px;margin-top:16px"><h3>Recent Orders (Payment to each restaurant owner)</h3>
{% for o in orders[:15] %}<div style="padding:10px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between"><span>#{{o.id}} - {{o.dish_name}} - ${{o.amount}} - Restaurant ID {{o.restaurant_id}} - User {{o.user_id}}</span><span>{{o.status}} {{o.created_at.strftime('%d/%m')}}</span></div>{% endfor %}
</div>
{% endif %}
{% if tab=='restaurants' %}
<div style="background:#fff;padding:20px;border-radius:16px">
<h3>Add New Restaurant (After you agree with owner)</h3>
<form method="POST" action="/admin/add-restaurant" style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
<input name="name" placeholder="Restaurant Name e.g. Chicken Inn" required>
<input name="location" placeholder="Location e.g. Samora Machel Ave" required>
<input name="phone" placeholder="Owner Phone / EcoCash number" required>
<input name="image" placeholder="Image URL (or leave empty)">
<input name="description" placeholder="Description" style="grid-column:1/3">
<input name="ecocash" placeholder="EcoCash / Payment details - e.g. EcoCash 077xxxxxx" style="grid-column:1/3">
<button class="btn btn-green" style="grid-column:1/3;margin-top:10px">Add Restaurant Portal</button>
</form></div>
<div class="rest-grid" style="margin-top:20px">
{% for r in rests %}<div style="background:#fff;border-radius:16px;overflow:hidden"><img src="{{r.image}}" style="width:100%;height:160px;object-fit:cover"><div style="padding:14px"><b>{{r.name}}</b><p style="font-size:13px;color:#666">{{r.location}}<br>📞 {{r.phone}}<br>EcoCash: {{r.ecocash_number}}<br>{{r.dishes|length}} dishes</p><a href="/restaurant/{{r.id}}" style="font-size:13px">View Portal</a> | <a href="/admin/del-restaurant/{{r.id}}" style="color:red;font-size:13px" onclick="return confirm('Delete restaurant?')">Delete</a></div></div>{% endfor %}
</div>
{% endif %}
{% if tab=='dishes' %}
<div style="background:#fff;padding:20px;border-radius:16px"><h3>Add Dish to Restaurant</h3>
<form method="POST" action="/admin/add-dish"><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
<select name="restaurant_id" required>{% for r in rests %}<option value="{{r.id}}">{{r.name}}</option>{% endfor %}</select>
<input name="name" placeholder="Dish name e.g. Burger" required>
<input name="price" type="number" step="0.01" placeholder="Price e.g. 5.5" required>
<input name="image" placeholder="Image URL">
</div><button class="btn btn-green" style="margin-top:10px">Add Dish</button></form></div>
<div class="menu-grid" style="margin-top:16px">
{% for d in dishes %}<div class="menu-card"><img src="{{d.image}}"><div style="padding:12px"><b>{{d.name}}</b> - ${{d.price}}<br><span style="font-size:12px;color:#666">{{d.restaurant.name if d.restaurant else 'No restaurant'}} - {{d.restaurant.location if d.restaurant else ''}}</span><br><a href="/admin/del-dish/{{d.id}}" style="color:red;font-size:12px">Delete</a></div></div>{% endfor %}
</div>
{% endif %}
{% if tab=='users' %}
<div style="background:#fff;padding:20px;border-radius:16px"><table style="width:100%;font-size:14px"><tr style="color:#888;text-align:left"><th>Email</th><th>Phone</th><th>Admin</th><th>Action</th></tr>{% for u in users %}<tr><td>{{u.email}}</td><td>{{u.phone}}</td><td>{{u.is_admin}}</td><td><a href="/admin/make-admin/{{u.id}}">Toggle Admin</a> | <a href="/admin/del-user/{{u.id}}" style="color:red">Delete</a></td></tr>{% endfor %}</table></div>
{% endif %}
{% if tab=='orders' %}
<div style="background:#fff;padding:20px;border-radius:16px"><h3>All Orders - Payment to each restaurant owner</h3>{% for o in orders %}<div style="padding:10px 0;border-bottom:1px solid #eee"><b>#{{o.id}} {{o.dish_name}} - ${{o.amount}}</b> - Restaurant {{o.restaurant_id}} - Status {{o.status}} - User {{o.user_id}} - {{o.created_at.strftime('%d/%m %H:%M')}} <a href="/admin/order-status/{{o.id}}" style="margin-left:10px">Next Status</a></div>{% endfor %}</div>
{% endif %}
</div>
""", tab=tab, users=users, rests=rests, dishes=dishes, orders=orders)

@app.route('/admin/add-restaurant', methods=['POST'])
@login_required
def add_rest():
    if not current_user.is_admin: return "Denied",403
    r=Restaurant(name=request.form['name'], location=request.form['location'], phone=request.form['phone'], image=request.form['image'] or 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500', description=request.form['description'] or 'Great food', ecocash_number=request.form['ecocash'] or 'To be added')
    db.session.add(r); db.session.commit(); return redirect('/admin?tab=restaurants')

@app.route('/admin/del-restaurant/<int:id>')
@login_required
def del_rest(id):
    if not current_user.is_admin: return "Denied",403
    r=Restaurant.query.get(id); 
    if r: 
        for d in r.dishes: db.session.delete(d)
        db.session.delete(r); db.session.commit()
    return redirect('/admin?tab=restaurants')

@app.route('/admin/add-dish', methods=['POST'])
@login_required
def add_dish():
    if not current_user.is_admin: return "Denied",403
    d=Dish(name=request.form['name'], price=float(request.form['price']), restaurant_id=int(request.form['restaurant_id']), image=request.form['image'] or 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500')
    db.session.add(d); db.session.commit(); return redirect('/admin?tab=dishes')

@app.route('/admin/del-dish/<int:id>')
@login_required
def del_dish(id):
    if not current_user.is_admin: return "Denied",403
    d=Dish.query.get(id); 
    if d: db.session.delete(d); db.session.commit()
    return redirect('/admin?tab=dishes')

@app.route('/admin/del-user/<int:id>')
@login_required
def del_user(id):
    if not current_user.is_admin or id==current_user.id: return redirect('/admin?tab=users')
    u=User.query.get(id); 
    if u: db.session.delete(u); db.session.commit()
    return redirect('/admin?tab=users')

@app.route('/admin/make-admin/<int:id>')
@login_required
def make_admin(id):
    if not current_user.is_admin: return "Denied",403
    u=User.query.get(id); 
    if u: u.is_admin=not u.is_admin; db.session.commit()
    return redirect('/admin?tab=users')

@app.route('/admin/order-status/<int:id>')
@login_required
def order_status(id):
    if not current_user.is_admin: return "Denied",403
    o=Order.query.get(id)
    if o: o.status={'Pending':'Preparing','Preparing':'Out for delivery','Out for delivery':'Delivered','Delivered':'Pending'}[o.status]; db.session.commit()
    return redirect('/admin?tab=orders')

if __name__=="__main__":
    app.run(host='0.0.0.0',port=10000)