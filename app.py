@app.route('/')
def home():
    dishes = [] # your existing query
    # keep your dishes = Dish.query.all() etc ABOVE this return
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,sans-serif}
body{background:#f8f8fa;color:#111}
.top{padding:14px 20px;display:flex;justify-content:space-between;align-items:center;background:#fff;border-bottom:1px solid #eee;position:sticky;top:0;z-index:10}
.logo{font-weight:800;font-size:18px;color:#e67e22}
.logo span{margin-right:6px}
.btn{padding:8px 16px;border-radius:20px;border:1px solid #ddd;background:#fff;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;color:#111}
.hero{background:linear-gradient(135deg,#ff8c00,#ff6a00);color:#fff;padding:36px 20px;text-align:center}
.hero h1{font-size:28px;font-weight:800;line-height:1.2}
.hero p{margin-top:8px;opacity:.95;font-size:15px}
.stats{display:flex;gap:12px;justify-content:center;margin-top:18px}
.stat{background:rgba(255,255,255,.18);backdrop-filter:blur(10px);padding:8px 14px;border-radius:12px;font-size:13px;font-weight:600}
.wrap{max-width:1100px;margin:0 auto;padding:24px 16px}
.empty{background:#fff;border:1px dashed #ddd;border-radius:16px;padding:60px 20px;text-align:center}
.empty .icon{font-size:42px;margin-bottom:12px}
.empty h3{font-size:16px}
.empty p{color:#777;font-size:13px;margin-top:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.card{background:#fff;border-radius:16px;overflow:hidden;border:1px solid #eee;box-shadow:0 2px 10px rgba(0,0,0,.04)}
.card img{width:100%;height:160px;object-fit:cover}
.card-body{padding:12px}
.price{color:#e67e22;font-weight:800}
.footer{margin-top:40px;background:#111;color:#aaa;padding:24px;text-align:center;font-size:12px}
.footer img{height:22px;vertical-align:middle;margin-right:6px}
</style>
</head>
<body>
<div class="top">
<div class="logo"><span>🍔</span> ZimMarket</div>
<div>
<a href="/login" class="btn">Login</a>
<a href="/register" class="btn" style="background:#111;color:#fff;border-color:#111;margin-left:6px">Register</a>
<a href="/my-orders" class="btn" style="margin-left:6px">My Orders</a>
</div>
</div>

<div class="hero">
<h1>Order • Pay EcoCash • Cancel Anytime</h1>
<p>Fast food delivery across Zimbabwe - order from your favorite spots</p>
<div class="stats">
<div class="stat">⚡ 30 min delivery</div>
<div class="stat">💰 EcoCash & USD</div>
<div class="stat">✅ Cancel anytime</div>
</div>
</div>

<div class="wrap">
<div class="empty">
<div class="icon">🍽️</div>
<h3>No dishes yet</h3>
<p>Restaurants will appear here once vendors add menus.<br>Be the first to list your food!</p>
<br>
<a href="/register" class="btn" style="background:#111;color:#fff">Become a Vendor</a>
</div>
</div>

<div class="footer">
<img src="/static/uploads/evex_logo.png"> Powered by Evex Tech • © 2026 ZimMarket<br>
Made for Zimbabwe 🇿🇼
</div>
</body>
</html>
'''