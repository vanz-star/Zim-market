@app.route('/register', methods=['GET','POST'])
def register():
    # ... keep your existing POST logic above this ...
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Inter,Arial,sans-serif;background:#f6f7fb;margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#fff;width:100%;max-width:380px;padding:28px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.08)}
h2{margin:0 0 20px;text-align:center}
label{display:block;font-size:13px;margin:12px 0 6px;color:#333;font-weight:600}
input{width:100%;padding:12px 14px;border:1px solid #ddd;border-radius:10px;box-sizing:border-box;font-size:14px}
input:focus{outline:none;border-color:#111;box-shadow:0 0 0 3px rgba(0,0,0,.08)}
button{width:100%;margin-top:20px;padding:12px;background:#111;color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer}
button:hover{background:#000}
.footer{text-align:center;margin-top:16px;font-size:13px}
a{color:#111;text-decoration:none}
</style>
</head>
<body>
<div class="card">
<h2>Create Account</h2>
<form method="POST">
<label>Full Name</label>
<input type="text" name="name" placeholder="John Doe" required>

<label>Email</label>
<input type="email" name="email" placeholder="you@example.com" required>

<label>Password</label>
<input type="password" name="password" placeholder="••••••••" required>

<button type="submit">Register</button>
</form>
<div class="footer">Already have an account? <a href="/login">Login</a></div>
</div>
</body>
</html>
'''