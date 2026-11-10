from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZimMarket - Sadza & More</title>
        <style>
            body { font-family: Arial; margin:0; background:#FFF8F0; }
            .header { background:#2E7D32; color:white; padding:20px; text-align:center; }
            .header h1 { margin:0; font-size:28px; }
            .container { padding:15px; max-width:500px; margin:auto; }
            .card { background:white; border-radius:15px; padding:15px; margin:15px 0; box-shadow:0 4px 10px rgba(0,0,0,0.1); }
            .card h3 { margin:5px 0; color:#2E7D32; }
            .price { color:#FF6F00; font-weight:bold; font-size:18px; }
            .btn { background:#2E7D32; color:white; border:none; padding:12px; width:100%; border-radius:10px; font-size:16px; font-weight:bold; }
            .btn:active { background:#1B5E20; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🇿🇼 ZimMarket</h1>
            <p>Fresh Sadza Delivered Fast!</p>
        </div>
        <div class="container">
            <div class="card">
                <h3>🍛 Sadza + Muriwo + Chicken</h3>
                <p>Traditional full meal, hot & fresh</p>
                <p class="price">$5.00</p>
                <button class="btn" onclick="order('Sadza + Muriwo + Chicken')">Order Now - WhatsApp</button>
            </div>
            <div class="card">
                <h3>🥬 Sadza + Muriwo</h3>
                <p>Healthy veggies with sadza</p>
                <p class="price">$3.00</p>
                <button class="btn" onclick="order('Sadza + Muriwo')">Order Now - WhatsApp</button>
            </div>
            <div class="card">
                <h3>🍗 Chicken Only</h3>
                <p>Grilled / Fried chicken pieces</p>
                <p class="price">$4.00</p>
                <button class="btn" onclick="order('Chicken Only')">Order Now - WhatsApp</button>
            </div>
        </div>
        <script>
            function order(item){
                window.open('https://wa.me/0783901528?text=Hi ZimMarket! I want to order: ' + item, '_blank');
            }
        </script>
    </body>
    </html>
    """

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=10000)
