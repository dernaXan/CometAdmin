from flask import request
from flask import Flask, make_response, render_template, redirect, session, url_for
import secrets, os
import requests

#vars
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = 'https://cometadmin-73ya.onrender.com/login_callback'
SCOPE = 'identify guilds'

API_BASE_URL = "https://discord.com/api"

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
app.secret_key = os.urandom(24)

@app.route('/')
def index():
  user = session.get("user", None)
  if not user:
    return render_template("not_logged_in.html")
  return render_template("admin_panel.html")

@app.route('/login')
def login():
  login_url = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE.replace(' ', '+')}"
  return redirect(login_url)

@app.route('/login_callback')
def logincallback():
  code = request.args.get("code")
  data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE
  }
  headers = {
    "Content-Type": "application/x-www-form-urlencoded"
  }
  r = requests.post(f"{API_BASE_URL}/oauth2/token", data=data, headers=headers)
  r.raise_for_status()
  token = r.json()["access_token"]

  user_data = requests.get(
    f"{API_BASE_URL}/users/@me",
    headers={"Authorization": f"Bearer {token}"}
  ).json()

  session["user"] = user_data
  return redirect(url_for("index"))

@app.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("index"))

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

