@app.route('/')
def home():
    try:
        dishes = Dish.query.all()
    except:
        dishes = []
    
    cards = ""
    if dishes:
        for d in dishes:
            n = str(getattr(d, 'name', 'Dish'))
            p = str(getattr(d, 'price', '5'))
            desc = str(getattr(d, 'description', 'Tasty meal'))[:55]
            img = str(getattr(d, 'image', ''))
            if not img or len(img) < 5:
                img = 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600'
            cards += '<div class="dish"><div class="dish-img"><img src="' + img + '"><button class="fav">♡</button><span class="time">25-35 min</span></div><div class="dish-info"><div class="dish-top"><h3>' + n + '</h3><span class="rating">★ 4.8</span></div><p class="dish-desc">' + desc + ' • Free delivery</p><div class="dish-bottom"><span class="dish-price">$' + p + '</span><button class="add">Add +</button></div></div></div>'
    else:
        cards = '<div class="empty-state"><div class="empty-icon">🍔</div><h2>Your city. Your food.</h2><p>No restaurants yet. Be the first vendor!</p><a href="/register" class="cta">Become a Vendor - Free</a></div>'

    page = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZimMarket - Food Delivery Zimbabwe</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial}
body{background:#f7f7f7}
.nav{position:sticky;top:0;z-index:10;background:#fff;border-bottom:1px solid #eee;padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:22px;letter-spacing:-0.5px}
.logo span{color:#06c167}
.search-bar{display:none}
@media(min-width:768px){.search-bar{display:flex;background:#f2f2f2;border-radius:24px;padding:10px 16px;gap:8px;flex:1;max-width:400px;margin:0 30px}.search-bar input{border:none;background:transparent;outline:none;width:100%}}
.btns{display:flex;gap:8px}
.btn{padding:9px 16px;border-radius:20px;border:none;font-weight:700;font-size:14px;text-decoration:none;cursor:pointer}
.btn-light{background:#f2f2f2;color:#111}
.btn-dark{background:#000;color:#fff}
.hero{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;max-width:1200px;margin:0 auto;padding:30px 20px;gap:20px;background:#fff}
.hero-text{flex:1;min-width:280px}
.hero-text h1{font-size:36px;font-weight:900;line-height:1.1;letter-spacing:-1px}
.hero-text h1 span{color:#06c167}
.hero-text p{margin:14px 0 20px;color:#666;font-size:16px}
.hero-input{display:flex;background:#fff;border:1px solid #ddd;border-radius:12px;overflow:hidden;max-width:420px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.hero-input input{flex:1;padding:14px;border:none;outline:none}
.hero-input button{background:#000;color:#fff;border:none;padding:0 22px;font-weight:700}
.cats{max-width:1200px;margin:10px auto;padding:0 20px;display:flex;gap:12px;overflow-x:auto}
.cat{white-space:nowrap;background:#fff;border:1px solid #eee;padding:10px 18px;border-radius:20px;font-weight:600;font-size:14px;cursor:pointer}
.cat.active{background:#000;color:#fff;border-color:#000}
.wrap{max-width:1200px;margin:0 auto;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.dish{background:#fff;border-radius:16px;overflow:hidden;border:1px solid #eee;transition:.2s}
.dish:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.08)}
.dish-img{position:relative;height:200px;background:#f5f5f5}
.dish-img img{width:100%;height:100%;object-fit:cover}
.fav{position:absolute;top:12px;right:12px;background:#fff;border:none;width:34px;height:34px;border-radius:50%;font-size:16px;cursor:pointer}
.time{position:absolute;bottom:10px;right:10px;background:#fff;padding:5px 10px;border-radius:20px;font-size:12px;font-weight:700}
.dish-info{padding:14px}
.dish-top{display:flex;justify-content:space-between;align-items:center}
.dish-top h3{font-size:16px;font-weight:700}
.rating{background:#f7f7f7;padding:4px 8px;border-radius:10px;font-size:12px;font-weight:700}
.dish-desc{color:#777;font-size:13px;margin:6px 0 12px}
.dish-bottom{display:flex;justify-content:space-between;align-items:center}
.dish-price{font-weight:800;font-size:16px}
.add{background:#06c167;color:#fff;border:none;padding:8px 16px;border-radius:20px;font-weight:700;cursor:pointer}
.empty-state{grid-column:1/-1;background:#fff;border-radius:20px;padding:60px 20px;text-align:center;border:1px dashed #ddd}
.empty-icon{font-size:48px;margin-bottom:12px}
.cta{display:inline-block;margin-top:16px;background:#000;color:#fff;padding:12px 22px;border-radius:20px;text-decoration:none;font-weight:700}
.footer{margin-top:50px;background:#000;color:#888;padding:30px 20px;text-align:center;font-size:13px}
</style>
</head>
<body>
<div class="nav"><div class="logo">Zim<span>Market</span></div><div class="search-bar">🔍 <input placeholder="Food, groceries, drinks, etc."></div><div class="btns"><a href="/login" class="btn btn-light">Log in</a><a href="/register" class="btn btn-dark">Sign up</a></div></div>
<div class="hero"><div class="hero-text"><h1>Food delivery and more <span>— Zimbabwe</span></h1><p>Groceries, alcohol and convenience products. Order • Pay EcoCash • Cancel anytime.</p><div class="hero-input"><input placeholder="Enter delivery address"><button>Find Food</button></div></div><img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400" style="width:360px;max-width:100%;border-radius:20px"></div>
<div class="cats"><div class="cat active">All</div><div class="cat">🍔 Burgers</div><div class="cat">🍕 Pizza</div><div class="cat">🍗 Chicken</div><div class="cat">🍜 Local</div><div class="cat">🥤 Drinks</div><div class="cat">🛒 Groceries</div></div>
<div class="wrap"><div class="grid">REPLACE_CARDS</div></div>
<div class="footer">© 2026 ZimMarket • Made with ❤️ by Evex Tech • Harare, Zimbabwe 🇿🇼<br>Powered by Evex Tech</div>
</body>
</html>
"""
    return page.replace("REPLACE_CARDS", cards)