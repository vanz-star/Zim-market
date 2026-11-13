from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    try:
        from models import Dish
        dishes = Dish.query.all()
        cards = ""
        for d in dishes:
            cards += f'<div style="border:1px solid #eee;padding:10px;border-radius:10px">{d.name} - ${d.price}</div>'
        if not cards:
            cards = '<p>No dishes yet - add in admin</p>'
    except:
        cards = '<p>Welcome! Food delivery in Zimbabwe</p>'

    page = """
<body>
<div class="nav"><div class="logo">Zim<span>Market</span></div><div class="search-bar">🔍 <input placeholder="Search Food"></div><div class="btns"><a href="/login" class="btn btn-light">Log in</a><a href="/register" class="btn btn-dark">Sign up</a></div></div>
<div class="hero"><div class="hero-text"><h1>Food delivery and more <span>— Zimbabwe</span></h1><p>Groceries, alcohol and convenience products. Order • Pay EcoCash • Cancel anytime.</p><div class="hero-input"><input placeholder="Enter delivery address"><button>Find Food</button></div><img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500" style="width:100%;border-radius:20px"></div></div>
<div class="cats"><div class="cat active">All</div><div class="cat">🍔 Burgers</div><div class="cat">🍗 Chicken</div><div class="cat">🥘 Local</div><div class="cat">🍹 Drinks</div><div class="cat">🛒 Grocery</div></div>
<div class="wrap"><div class="grid">REPLACE_CARDS</div></div>
<div class="footer">© 2026 ZimMarket • Made with ❤️ by Evex Tech • Harare, Zimbabwe zw<br>Powered by Render</div>
<style>
body{margin:0;font-family:Inter,system-ui;background:#f7f7f7}
.nav{display:flex;justify-content:space-between;padding:14px 20px;background:#fff;align-items:center;position:sticky;top:0;z-index:10}
.logo{font-weight:900;font-size:22px} .logo span{color:#06c167}
.search-bar{background:#f0f0f0;padding:8px 12px;border-radius:20px} .search-bar input{border:0;background:transparent;outline:none}
.btn{padding:8px 16px;border-radius:20px;text-decoration:none;font-weight:600} .btn-light{background:#eee;color:#000} .btn-dark{background:#000;color:#fff}
.hero{display:flex;padding:30px;gap:20px;background:#fff} .hero-text h1{font-size:48px;line-height:1} .hero-text span{color:#666} .hero-input{display:flex;background:#f0f0f0;border-radius:10px;padding:5px;margin:15px 0} .hero-input input{flex:1;border:0;background:transparent;padding:10px;outline:none} .hero-input button{background:#000;color:#fff;border:0;padding:10px 20px;border-radius:8px}
.cats{display:flex;gap:10px;padding:15px 20px;overflow:auto} .cat{background:#fff;padding:8px 14px;border-radius:20px;white-space:nowrap} .cat.active{background:#000;color:#fff}
.wrap{padding:20px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px}
.footer{text-align:center;padding:30px;color:#888}
</style>
</body>
</html>
    """
    return page.replace("REPLACE_CARDS", cards)

if __name__ == "__main__":
    app.run()