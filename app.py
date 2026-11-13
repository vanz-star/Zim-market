from flask import Flask, render_template_string, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, date, time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tableahead-clean-v4'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tableahead.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ===== DATABASE MODELS =====
class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)
    phone=db.Column(db.String(20), nullable=False)
    password_hash=db.Column(db.String(200), nullable=False)
    is_admin=db.Column(db.Boolean, default=False)

class Restaurant(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), unique=True)
    location=db.Column(db.String(200), default='Harare')
    phone=db.Column(db.String(20), default='0770000000')
    image=db.Column(db.String(500), default='https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600')
    ecocash=db.Column(db.String(100), default='EcoCash to be set after agreement')

class Supplier(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    restaurant_id=db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    name=db.Column(db.String(100))
    phone=db.Column(db.String(20))
    category=db.Column(db.String(50))
    last_price_note=db.Column(db.String(200), default='')

class Ingredient(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    restaurant_id=db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    name=db.Column(db.String(100))
    unit=db.Column(db.String(20), default='kg')
    current_qty=db.Column(db.Float, default=0)
    min_qty=db.Column(db.Float, default=5)
    cost_per_unit=db.Column(db.Float, default=0)
    supplier_id=db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    supplier=db.relationship('Supplier')

class Dish(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    restaurant_id=db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    name=db.Column(db.String(100))
    price=db.Column(db.Float)
    image=db.Column(db.String(500), default='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500')
    restaurant=db.relationship('Restaurant', backref='dishes')

class Recipe(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    dish_id=db.Column(db.Integer, db.ForeignKey('dish.id'))
    ingredient_id=db.Column(db.Integer, db.ForeignKey('ingredient.id'))
    qty_needed=db.Column(db.Float)
    dish=db.relationship('Dish', backref='recipes')
    ingredient=db.relationship('Ingredient')

class Booking(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    restaurant_id=db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    type=db.Column(db.String(20)) # Table or Preorder
    date=db.Column(db.Date)
    time=db.Column(db.String(20))
    people=db.Column(db.Integer, default=2)
    dish_name=db.Column(db.String(100), nullable=True)
    qty=db.Column(db.Integer, default=1)
    notes=db.Column(db.String(300))
    status=db.Column(db.String(20), default='Pending')
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    restaurant_id=db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    supplier_id=db.Column(db.Integer, db.ForeignKey('supplier.id'))
    ingredient_name=db.Column(db.String(100))
    qty=db.Column(db.Float)
    total_cost=db.Column(db.Float)
    invoice_no=db.Column(db.String(50))
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@zimmarket.co.zw').first():
        db.session.add(User(email='admin@zimmarket.co.zw', phone='0770000000', password_hash=generate_password_hash('Admin123!'), is_admin=True))
        db.session.commit()
    if Restaurant.query.count()==0:
        r=Restaurant(name='Chicken Inn', location='Samora Machel Ave, Harare CBD', phone='0291234567', ecocash='0771234567 - EcoCash (To be set)', image='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600')
        db.session.add(r); db.session.commit()
        s1=Supplier(restaurant_id=r.id, name="Irvine's Chickens", phone='0772000001', category='Chicken', last_price_note='Chicken $4.5/kg stable')
        s2=Supplier(restaurant_id=r.id, name='MegaMarket', phone='0772000002', category='General', last_price_note='Tomatoes up 30% this month!')
        s3=Supplier(restaurant_id=r.id, name='Delta Beverages', phone='0772000003', category='Drinks', last_price_note='Coke price stable')
        db.session.add_all([s1,s2,s3]); db.session.commit()
        i1=Ingredient(restaurant_id=r.id, name='Chicken Breast', unit='kg', current_qty=10, min_qty=5, cost_per_unit=4.5, supplier_id=s1.id)
        i2=Ingredient(restaurant_id=r.id, name='Burger Buns', unit='pcs', current_qty=50, min_qty=20, cost_per_unit=0.1, supplier_id=s2.id)
        i3=Ingredient(restaurant_id=r.id, name='Lettuce', unit='kg', current_qty=2, min_qty=2, cost_per_unit=2, supplier_id=s2.id)
        i4=Ingredient(restaurant_id=r.id, name='Tomatoes', unit='kg', current_qty=1, min_qty=3, cost_per_unit=3, supplier_id=s2.id)
        db.session.add_all([i1,i2,i3,i4]); db.session.commit()
        d1=Dish(restaurant_id=r.id, name='Chicken Burger', price=5.5, image='https://images.unsplash.com/photo-1568909344668-6f14a07b56a0?w=500')
        d2=Dish(restaurant_id=r.id, name='2 Piece & Chips', price=6.5, image='https://images.unsplash.com/photo-1626645738196-c2a046020eb6?w=500')
        db.session.add_all([d1,d2]); db.session.commit()
        db.session.add_all([Recipe(dish_id=d1.id, ingredient_id=i1.id, qty_needed=0.2), Recipe(dish_id=d1.id, ingredient_id=i2.id, qty_needed=1), Recipe(dish_id=d1.id, ingredient_id=i3.id, qty_needed=0.02)])
        db.session.commit()

CSS="""<style>*{font-family:Inter,system-ui;margin:0} body{background:#f7f7f7} .nav{display:flex;justify-content:space-between;padding:14px 20px;background:#fff;position:sticky;top:0;z-index:10;box-shadow:0 1px 4px rgba(0,0,0,.06)} .logo{font-weight:900;font-size:20px;text-decoration:none;color:#000} .logo span{color:#06c167} .btn{padding:9px 16px;border-radius:20px;text-decoration:none;font-weight:600;font-size:13px;border:0;cursor:pointer;display:inline-block} .btn-dark{background:#000;color:#fff} .btn-light{background:#eee;color:#000} .btn-green{background:#06c167;color:#fff} .wrap{max-width:1100px;margin:0 auto;padding:16px} .card{background:#fff;border-radius:14px;padding:16px;box-shadow:0 1px 6px rgba(0,0,0,.05);margin-bottom:14px} input,select,textarea{padding:10px;border:1px solid #ddd;border-radius:8px;margin:4px 0;width:100%;font-size:14px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px} .low{background:#fff3cd;border:1px solid #ffc107;padding:8px;border-radius:8px;font-size:13px;margin:6px 0} .out{background:#f8d7da;border:1px solid #dc3545} table{width:100%;font-size:13px;border-collapse:collapse} th{color:#888;text-align:left;padding:8px} td{padding:8px;border-top:1px solid #eee}</style>"""

def is_admin(): return current_user.is_authenticated and current_user.is_admin

@app.route('/')
def home():
    rests=Restaurant.query.all()
    return render_template_string(CSS+"""
<div class="nav"><a href="/" class="logo">TABLEAHEAD <span>OS</span></a><div>{% if current_user.is_authenticated %}<span style="font-size:12px">{{current_user.email.split('@')[0]}}</span> {% if is_admin() %}<a href="/admin" class="btn btn-green">Admin OS</a>{% endif %} <a href="/logout" class="btn btn-light">Logout</a>{% else %}<a href="/login" class="btn btn-light">Login</a> <a href="/signup" class="btn btn-dark">Sign up</a>{% endif %}</div></div>
<div style="background:#fff;padding:28px 20px"><h1 style="font-size:38px;font-weight:900">Front: Menu, Booking, Pre-order</h1><p style="color:#666;margin-top:6px">Click restaurant → See its portal → Book table or Pre-order food for tomorrow. System checks stock automatically.</p></div>
<div class="wrap"><div class="grid">{% for r in rests %}<a href="/restaurant/{{r.id}}" style="text-decoration:none;color:#000"><div class="card" style="padding:0;overflow:hidden"><img src="{{r.image}}" style="width:100%;height:180px;object-fit:cover"><div style="padding:14px"><b style="font-size:18px">{{r.name}}</b><p style="font-size:13px;color:#666">{{r.location}} • {{r.phone}}<br>💰 {{r.ecocash}} • {{r.dishes|length}} dishes</p></div></div></a>{% endfor %}</div></div>
""")

@app.route('/restaurant/<int:id>', methods=['GET','POST'])
def restaurant(id):
    r=Restaurant.query.get_or_404(id)
    ingredients=Ingredient.query.filter_by(restaurant_id=id).all()
    low=[i for i in ingredients if i.current_qty <= i.min_qty]
    return render_template_string(CSS+"""
<div class="nav"><a href="/" class="logo">TABLEAHEAD</a><a href="/" class="btn btn-light">← All Restaurants</a></div>
<div class="wrap">
<div style="display:grid;grid-template-columns:360px 1fr;gap:16px">
<div>
<div class="card" style="padding:0;overflow:hidden"><img src="{{r.image}}" style="width:100%;height:200px;object-fit:cover"><div style="padding:14px"><h2>{{r.name}}</h2><p style="font-size:13px;color:#666">📍 {{r.location}}<br>📞 {{r.phone}}<br>💰 Payment to owner: {{r.ecocash}}<br><br>Stock check before pre-order: System verifies ingredients.</p></div></div>
<div class="card"><h4>Stock Status</h4>{% for i in ingredients %}<div class="{{'out low' if i.current_qty==0 else 'low' if i.current_qty<=i.min_qty else ''}}" style="padding:6px 8px;margin:4px 0;border-radius:6px;background:{{'#fff3cd' if i.current_qty<=i.min_qty and i.current_qty>0 else '#f8d7da' if i.current_qty==0 else '#e8f8f0'}};font-size:12px">{{i.name}}: {{i.current_qty}}{{i.unit}} / min {{i.min_qty}}{{i.unit}} - {{'OUT!' if i.current_qty==0 else 'LOW' if i.current_qty<=i.min_qty else 'OK'}}</div>{% endfor %}</div>

<div class="card"><h4>1. Book Table</h4><form method="POST" action="/book/{{r.id}}"><input type="hidden" name="type" value="Table"><input type="date" name="date" required><input type="time" name="time" value="19:00" required><input type="number" name="people" placeholder="People e.g. 4" required><textarea name="notes" placeholder="Notes e.g. Window seat"></textarea><button class="btn btn-dark" style="width:100%;margin-top:6px">Book Table</button></form></div>
</div>

<div>
<h3>2. Pre-Order Menu - Stock auto deducts</h3><p style="font-size:13px;color:#666">Customer pre-orders 4x Rump Steak at 13:30 tomorrow → System checks steak & veg → If not enough → Adds to shopping list → Chef sees prep list</p>
<div class="grid" style="margin-top:12px">
{% for d in r.dishes %}
<div class="card" style="padding:0;overflow:hidden"><img src="{{d.image}}" style="width:100%;height:140px;object-fit:cover"><div style="padding:12px"><b>{{d.name}} - ${{d.price}}</b><br><span style="font-size:11px;color:#666">Uses: {% for rec in d.recipes %}{{rec.ingredient.name}} {{rec.qty_needed}}{{rec.ingredient.unit}} {% endfor %}</span>
<form method="POST" action="/book/{{r.id}}" style="margin-top:8px;display:grid;grid-template-columns:1fr 1fr;gap:6px">
<input type="hidden" name="type" value="Preorder"><input type="hidden" name="dish_name" value="{{d.name}}"><input type="date" name="date" required><input type="time" name="time" value="13:30" required><input type="number" name="qty" placeholder="Qty e.g. 4" value="1" required><input type="number" name="people" placeholder="People" value="1"><button class="btn btn-green" style="grid-column:1/3">Pre-order for date - Check Stock</button>
</form>
</div></div>
{% endfor %}
</div>
<div class="card" style="margin-top:16px"><h4>Recent Bookings/Pre-orders</h4>{% for b in bookings %}<div style="padding:6px 0;border-bottom:1px solid #eee;font-size:13px"><b>{{b.type}}</b> - {{b.dish_name or ''}} x{{b.qty}} - {{b.date}} {{b.time}} - {{b.people}} people - {{b.status}}</div>{% endfor %}</div>
</div>
</div>
</div>
""", r=r, ingredients=ingredients, low=low, bookings=Booking.query.filter_by(restaurant_id=id).order_by(Booking.created_at.desc()).limit(10).all())

@app.route('/book/<int:rid>', methods=['POST'])
@login_required
def book(rid):
    r=Restaurant.query.get(rid)
    btype=request.form['type']; dname=request.form.get('dish_name'); qty=int(request.form.get('qty',1))
    # STOCK CHECK FOR PREORDER
    message="Booked"
    if btype=='Preorder' and dname:
        dish=Dish.query.filter_by(restaurant_id=rid, name=dname).first()
        if dish:
            can_make=True
            for rec in dish.recipes:
                if rec.ingredient.current_qty < rec.qty_needed*qty: can_make=False
            if not can_make:
                message="Not enough stock - Added to shopping list!"
            else:
                for rec in dish.recipes:
                    rec.ingredient.current_qty -= rec.qty_needed*qty
    b=Booking(restaurant_id=rid, user_id=current_user.id, type=btype, date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(), time=request.form['time'], people=int(request.form.get('people',1)), dish_name=dname, qty=qty, notes=request.form.get('notes',''), status=message)
    db.session.add(b); db.session.commit()
    return redirect(f'/restaurant/{rid}')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        e=request.form['email'].lower().strip(); ph=request.form['phone']; pw=request.form['password']
        if not User.query.filter_by(email=e).first():
            u=User(email=e, phone=ph, password_hash=generate_password_hash(pw)); db.session.add(u); db.session.commit(); login_user(u); return redirect('/')
    return render_template_string(CSS+"""<div class="nav"><a href="/" class="logo">TABLEAHEAD</a></div><div class="wrap" style="max-width:400px"><div class="card"><h3>Sign up - Email, Phone, Password</h3><form method="POST"><input name="email" type="email" placeholder="Email" required><input name="phone" placeholder="Phone 077..." required><input name="password" type="password" placeholder="Password" required><button class="btn btn-dark" style="width:100%;margin-top:8px">Sign up</button></form><p style="font-size:11px;margin-top:10px;background:#f0f0f0;padding:8px;border-radius:6px">Admin: admin@zimmarket.co.zw / Admin123!</p></div></div>""")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        e=request.form['email'].lower().strip(); pw=request.form['password']; u=User.query.filter_by(email=e).first()
        if u and check_password_hash(u.password_hash, pw): login_user(u); return redirect('/admin' if u.is_admin else '/')
    return render_template_string(CSS+"""<div class="nav"><a href="/" class="logo">TABLEAHEAD</a></div><div class="wrap" style="max-width:400px"><div class="card"><h3>Login</h3><form method="POST"><input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Password" required><button class="btn btn-dark" style="width:100%;margin-top:8px">Login</button></form></div></div>""")

@app.route('/logout')
def logout(): logout_user(); return redirect('/')

@app.route('/admin')
@login_required
def admin():
    if not is_admin(): return "Admin only",403
    tab=request.args.get('tab','front'); rid=request.args.get('rid',1,type=int)
    rests=Restaurant.query.all(); r=Restaurant.query.get(rid) if rests else None
    if not r and rests: r=rests[0]; rid=r.id
    ingredients=Ingredient.query.filter_by(restaurant_id=rid).all() if r else []
    suppliers=Supplier.query.filter_by(restaurant_id=rid).all() if r else []
    dishes=Dish.query.filter_by(restaurant_id=rid).all() if r else []
    bookings=Booking.query.filter_by(restaurant_id=rid).order_by(Booking.created_at.desc()).all() if r else []
    purchases=Purchase.query.filter_by(restaurant_id=rid).order_by(Purchase.created_at.desc()).all() if r else []
    low=[i for i in ingredients if i.current_qty<=i.min_qty]
    return render_template_string(CSS+"""
<div class="nav"><a href="/" class="logo">TABLEAHEAD <span>OS - CLEAN</span></a><div><a href="/" class="btn btn-light">Site</a> <a href="/logout" class="btn btn-dark">Logout</a></div></div>
<div class="wrap">
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
<select onchange="location='/admin?tab='+tab+'&rid='+this.value" style="width:180px"><script>var tab="{{tab}}"</script>{% for rest in rests %}<option value="{{rest.id}}" {{'selected' if rest.id==rid else ''}}>{{rest.name}}</option>{% endfor %}</select>
<a href="/admin?tab=front&rid={{rid}}" class="btn {{'btn-dark' if tab=='front' else 'btn-light'}}">Front: Bookings</a>
<a href="/admin?tab=stock&rid={{rid}}" class="btn {{'btn-dark' if tab=='stock' else 'btn-light'}}">A. Stock {% if low %}🔴{{low|length}}{% endif %}</a>
<a href="/admin?tab=suppliers&rid={{rid}}" class="btn {{'btn-dark' if tab=='suppliers' else 'btn-light'}}">C. Suppliers & Purchases</a>
<a href="/admin?tab=menu&rid={{rid}}" class="btn {{'btn-dark' if tab=='menu' else 'btn-light'}}">Menu/Recipes</a>
</div>

{% if tab=='front' %}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div class="card"><h3>Today's Bookings & Pre-orders</h3><p style="font-size:12px;color:#666">Example: Customer pre-orders 4x Rump Steak at 13:30 tomorrow → System checked stock → Chef prep list</p><table><tr><th>Type</th><th>Date/Time</th><th>Dish xQty</th><th>People</th><th>Status</th></tr>{% for b in bookings %}<tr><td>{{b.type}}</td><td>{{b.date}} {{b.time}}</td><td>{{b.dish_name}} x{{b.qty}}</td><td>{{b.people}}</td><td>{{b.status}}</td></tr>{% endfor %}</table></div><div class="card"><h3>Chef Prep List (from pre-orders)</h3>{% for b in bookings if b.type=='Preorder' %}<div style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px">Tomorrow {{b.time}}: <b>{{b.qty}}x {{b.dish_name}}</b> for {{b.people}} people<br><span style="font-size:11px;color:#666">Check: {% for d in dishes if d.name==b.dish_name %}{% for rec in d.recipes %}{{rec.ingredient.name}} {{rec.qty_needed*b.qty}}{{rec.ingredient.unit}} {% endfor %}{% endfor %}</span></div>{% endfor %}</div></div>
{% endif %}

{% if tab=='stock' %}
<div class="card"><h3>A. Stock & Auto Re-ordering - Every Chicken Burger deducts: -1 bun, -0.2kg chicken</h3><form method="POST" action="/admin/add-ing?rid={{rid}}" style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:6px"><input name="name" placeholder="Ingredient e.g. Chicken" required><input name="unit" placeholder="kg/pcs" required><input name="qty" type="number" step="0.01" placeholder="Current Qty" required><input name="min" type="number" step="0.01" placeholder="Min Qty" required><input name="cost" type="number" step="0.01" placeholder="Cost/unit" required><select name="supplier_id"><option value="">Supplier</option>{% for s in suppliers %}<option value="{{s.id}}">{{s.name}}</option>{% endfor %}</select><button class="btn btn-green">Add</button></form></div>
{% if low %}<div class="card" style="border:2px solid #ffc107"><h3>⚠️ Auto-Alert: Stock Low - Dashboard shows "You have X left = Y days"</h3>{% for i in low %}<div class="low {{'out' if i.current_qty==0 else ''}}">🔴 {{i.name}}: {{i.current_qty}}{{i.unit}} left (min {{i.min_qty}}{{i.unit}}) = {% if i.current_qty==0 %}OUT OF STOCK{% else %}{{(i.current_qty/i.min_qty*2)|int}} days left{% endif %} → Supplier: {{i.supplier.name if i.supplier else 'None'}} <a href="https://wa.me/{{i.supplier.phone if i.supplier else '263772000001'}}?text=Hi%20{{i.supplier.name if i.supplier else ''}}%20Need%20{{i.min_qty*2 - i.current_qty}}{{i.unit}}%20{{i.name}}%20for%20{{r.name}}" target="_blank" class="btn btn-green" style="padding:4px 8px;margin-left:8px">One-tap WhatsApp {{i.supplier.name if i.supplier else ''}}</a></div>{% endfor %}</div>{% endif %}
<div class="card"><h3>All Stock - Auto shopping list generated</h3><table><tr><th>Ingredient</th><th>Qty</th><th>Min</th><th>Cost</th><th>Days Left</th><th>Supplier</th><th>Action</th></tr>{% for i in ingredients %}<tr style="{{'background:#fff3cd' if i.current_qty<=i.min_qty else ''}}"><td>{{i.name}}</td><td>{{i.current_qty}}{{i.unit}}</td><td>{{i.min_qty}}{{i.unit}}</td><td>${{i.cost_per_unit}}</td><td>{% if i.current_qty==0 %}0 - OUT{% else %}{{(i.current_qty/i.min_qty*2)|int}} days{% endif %}</td><td>{{i.supplier.name if i.supplier else '-'}}</td><td><a href="/admin/restock/{{i.id}}?rid={{rid}}" class="btn btn-light" style="padding:2px 6px">+10</a> <a href="/admin/del-ing/{{i.id}}?rid={{rid}}" style="color:red">Del</a></td></tr>{% endfor %}</table></div>
{% endif %}

{% if tab=='suppliers' %}
<div class="card"><h3>C. Supplier & Purchases - List of suppliers: Mega Markets, Delta, Irvine's</h3><form method="POST" action="/admin/add-sup?rid={{rid}}" style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px"><input name="name" placeholder="Name e.g. Irvine's" required><input name="phone" placeholder="Phone 077..." required><input name="category" placeholder="Chicken/General/Drinks" required><input name="note" placeholder="Price note e.g. Tomatoes up 30%"><button class="btn btn-green" style="grid-column:1/5">Add Supplier</button></form></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div class="card"><h3>Suppliers - One-click reorder</h3><table><tr><th>Name</th><th>Phone</th><th>Category</th><th>Note / Price Track</th><th>Reorder</th></tr>{% for s in suppliers %}<tr><td>{{s.name}}</td><td>{{s.phone}}</td><td>{{s.category}}</td><td style="font-size:11px">{{s.last_price_note}}</td><td><a href="https://wa.me/{{s.phone}}?text=Hi%20{{s.name}}%20Need%20restock%20for%20{{r.name}}%20-%20{{low|length}}%20items%20low" target="_blank" class="btn btn-green" style="padding:4px 8px">WhatsApp</a> <a href="/admin/del-sup/{{s.id}}?rid={{rid}}" style="color:red">Del</a></td></tr>{% endfor %}</table></div>
<div class="card"><h3>Purchases & Invoices - Tracks who is expensive</h3><form method="POST" action="/admin/add-purchase?rid={{rid}}" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px"><select name="supplier_id" required>{% for s in suppliers %}<option value="{{s.id}}">{{s.name}}</option>{% endfor %}</select><input name="ing" placeholder="Ingredient e.g. Tomatoes" required><input name="qty" type="number" step="0.01" placeholder="Qty" required><input name="cost" type="number" step="0.01" placeholder="Total Cost $" required><input name="invoice" placeholder="Invoice No"><button class="btn btn-dark">Add Purchase Invoice</button></form><table style="margin-top:10px"><tr><th>Date</th><th>Supplier</th><th>Item</th><th>Qty</th><th>Cost</th><th>Invoice</th></tr>{% for p in purchases %}<tr><td>{{p.created_at.strftime('%d/%m')}}</td><td>{{p.supplier_id}}</td><td>{{p.ingredient_name}}</td><td>{{p.qty}}</td><td>${{p.total_cost}}</td><td>{{p.invoice_no}}</td></tr>{% endfor %}</table><p style="font-size:11px;color:#666;margin-top:8px">Shows: "Tomatoes went up 30% this month" - compare last_price_note</p></div></div>
{% endif %}

{% if tab=='menu' %}
<div class="card"><h3>Menu + Recipe Mapping - Link dish to ingredients</h3><form method="POST" action="/admin/add-dish?rid={{rid}}" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px"><input name="name" placeholder="Dish name" required><input name="price" type="number" step="0.01" placeholder="Price $" required><input name="image" placeholder="Image URL"><button class="btn btn-green">Add Dish</button></form>
<form method="POST" action="/admin/add-recipe?rid={{rid}}" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:12px;border-top:1px solid #eee;padding-top:12px"><select name="dish_id">{% for d in dishes %}<option value="{{d.id}}">{{d.name}}</option>{% endfor %}</select><select name="ing_id">{% for i in ingredients %}<option value="{{i.id}}">{{i.name}} ({{i.current_qty}}{{i.unit}})</option>{% endfor %}</select><input name="qty" type="number" step="0.001" placeholder="Qty needed e.g. 0.2" required><button class="btn btn-dark">Link: Dish uses Ingredient</button></form></div>
<div class="grid">{% for d in dishes %}<div class="card"><b>{{d.name}} - ${{d.price}}</b><br><span style="font-size:11px">{% for rec in d.recipes %}{{rec.ingredient.name}} {{rec.qty_needed}}{{rec.ingredient.unit}} | {% endfor %}</span><br><a href="/admin/del-dish/{{d.id}}?rid={{rid}}" style="color:red;font-size:12px">Delete</a></div>{% endfor %}</div>
{% endif %}

</div>
""", tab=tab, rid=rid, rests=rests, r=r, ingredients=ingredients, suppliers=suppliers, dishes=dishes, bookings=bookings, purchases=purchases, low=low)

@app.route('/admin/add-ing', methods=['POST'])
@login_required
def add_ing(): rid=request.args.get('rid',1,type=int); i=Ingredient(restaurant_id=rid, name=request.form['name'], unit=request.form['unit'], current_qty=float(request.form['qty']), min_qty=float(request.form['min']), cost_per_unit=float(request.form['cost']), supplier_id=int(request.form['supplier_id']) if request.form['supplier_id'] else None); db.session.add(i); db.session.commit(); return redirect(f'/admin?tab=stock&rid={rid}')
@app.route('/admin/del-ing/<int:id>')
@login_required
def del_ing(id): rid=request.args.get('rid',1,type=int); db.session.delete(Ingredient.query.get(id)); db.session.commit(); return redirect(f'/admin?tab=stock&rid={rid}')
@app.route('/admin/restock/<int:id>')
@login_required
def restock(id): rid=request.args.get('rid',1,type=int); i=Ingredient.query.get(id); i.current_qty+=10; db.session.commit(); return redirect(f'/admin?tab=stock&rid={rid}')
@app.route('/admin/add-sup', methods=['POST'])
@login_required
def add_sup(): rid=request.args.get('rid',1,type=int); s=Supplier(restaurant_id=rid, name=request.form['name'], phone=request.form['phone'], category=request.form['category'], last_price_note=request.form['note']); db.session.add(s); db.session.commit(); return redirect(f'/admin?tab=suppliers&rid={rid}')
@app.route('/admin/del-sup/<int:id>')
@login_required
def del_sup(id): rid=request.args.get('rid',1,type=int); db.session.delete(Supplier.query.get(id)); db.session.commit(); return redirect(f'/admin?tab=suppliers&rid={rid}')
@app.route('/admin/add-purchase', methods=['POST'])
@login_required
def add_purchase(): rid=request.args.get('rid',1,type=int); p=Purchase(restaurant_id=rid, supplier_id=int(request.form['supplier_id']), ingredient_name=request.form['ing'], qty=float(request.form['qty']), total_cost=float(request.form['cost']), invoice_no=request.form['invoice']); db.session.add(p); db.session.commit(); return redirect(f'/admin?tab=suppliers&rid={rid}')
@app.route('/admin/add-dish', methods=['POST'])
@login_required
def add_dish(): rid=request.args.get('rid',1,type=int); d=Dish(restaurant_id=rid, name=request.form['name'], price=float(request.form['price']), image=request.form['image'] or 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500'); db.session.add(d); db.session.commit(); return redirect(f'/admin?tab=menu&rid={rid}')
@app.route('/admin/add-recipe', methods=['POST'])
@login_required
def add_recipe(): rid=request.args.get('rid',1,type=int); r=Recipe(dish_id=int(request.form['dish_id']), ingredient_id=int(request.form['ing_id']), qty_needed=float(request.form['qty'])); db.session.add(r); db.session.commit(); return redirect(f'/admin?tab=menu&rid={rid}')
@app.route('/admin/del-dish/<int:id>')
@login_required
def del_dish(id): rid=request.args.get('rid',1,type=int); db.session.delete(Dish.query.get(id)); db.session.commit(); return redirect(f'/admin?tab=menu&rid={rid}')

if __name__=="__main__": app.run(host='0.0.0.0', port=10000)