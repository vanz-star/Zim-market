from flask import Flask
import os
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Welcome to ZimMarket!</h1><h2>All Phones Can Access This!</h2><p>Order: Sadza, Muriwo, Chicken</p><button>Order Now</button>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
