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

def get_user_admin_guilds(user_id):
  r = requests.get(f"https://dcbot-cr1m.onrender.com/user/{user_id}/admin_guilds")
  return r.json()

def get_guild_roles(guild_id):
  r = requests.get(f"https://dcbot-cr1m.onrender.com/guild/{guild_id}/roles")
  return r.json()

def get_guild_channels(guild_id):
  r = requests.get(f"https://dcbot-cr1m.onrender.com/guild/{guild_id}/channels")
  return r.json()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
  user = session.get("user", None)
  if not user:
    return render_template("not_logged_in.html")
  guilds = get_user_admin_guilds(user_id = session.get("user", {}).get("id"))
  return render_template("server_select.html", guilds=guilds)

@app.route('/config/<guild_id>', methods=["GET", "POST"])
def config_guild(guild_id):
    user = session.get("user", None)
    if not user:
        return redirect(url_for("index"))

    guilds = get_user_admin_guilds(user_id=user.get("id"))
    # Prüfen, ob user admin in guild_id ist (optional)
    if not any(str(g['id']) == guild_id for g in guilds):
        return "Keine Berechtigung für diesen Server", 403

    roles = get_guild_roles(guild_id)
    channels = get_guild_channels(guild_id)

    if request.method == "POST":
        # Hier kannst du deine Formularverarbeitung machen
        # z.B. request.form['mod_role'], request.form['mod_channel'], etc.
        # Daten speichern und danach evtl. zurück zur Auswahl oder Bestätigung
        return redirect(url_for("config_guild", guild_id=guild_id))

    return render_template("guild_config.html", guild_id=guild_id, roles=roles, channels=channels)

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

