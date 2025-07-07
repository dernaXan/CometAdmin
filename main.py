from flask import request
from flask import Flask, make_response, render_template
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

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

@app.route('login')
def login():
  pass

@app.route('login-callback')
def logincallback():
  code = request.args.get("code")
  return "."
