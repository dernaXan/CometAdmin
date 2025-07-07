from flask import request
from flask import Flask, make_response, render_template, redirect
import secrets, os
#intern
def set_cookie(cookie, lifetime=604800, secure=False):
  for key, value in cookies.items():
    try:
      resp.set_cookie(key, value)
    except:
      resp = make_response(f"Cookies: {cookie}")
      resp.set_cookie(key, value, secure=secure, httponly=secure)

def get_cookie(key):
  data = request.cookies.get(key)
  return data

app = Flask(__name__)

@app.route('/')
def index():
  if get_cookie('session'):
    return 'Hallo'
  else:
    return render_template("not_logged_in.html")

@app.route('/login')
def login():
  login_url = "https://discord.com/oauth2/authorize?client_id=1391110692223848571&response_type=code&redirect_uri=https%3A%2F%2Fcometadmin-73ya.onrender.com%2Flogin_callback&scope=guilds+identify"
  return redirect(login_url)

@app.route('/login-callback')
def logincallback():
  code = request.args.get("code")
  return "."

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

