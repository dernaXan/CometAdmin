from flask import request, Flask, make_response, render_template, redirect, session, url_for
import secrets, os
import requests

# -----------------------------
# Variablen
# -----------------------------
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = 'https://cometadmin-73ya.onrender.com/login_callback'
SCOPE = 'identify guilds'
API_BASE_URL = "https://discord.com/api"
API_TOKEN = os.environ.get("API_TOKEN")

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)

# -----------------------------
# Hilfsfunktionen
# -----------------------------
def set_cookie(resp, cookies_dict, lifetime=604800, secure=False):
    for key, value in cookies_dict.items():
        resp.set_cookie(key, value, max_age=lifetime, secure=secure, httponly=True)
    return resp

def get_cookie(key):
    return request.cookies.get(key)

def get_user_admin_guilds(user_id):
    r = requests.get(f"https://dcbot-cr1m.onrender.com/user/{user_id}/admin_guilds")
    return r.json()

def get_guild_roles(guild_id):
    r = requests.get(f"https://dcbot-cr1m.onrender.com/guild/{guild_id}/roles")
    return r.json()

def get_guild_channels(guild_id):
    r = requests.get(f"https://dcbot-cr1m.onrender.com/guild/{guild_id}/channels")
    return r.json()

# -----------------------------
# Routen
# -----------------------------
@app.route('/')
def index():
    user = session.get("user", None)
    if not user:
        return render_template("not_logged_in.html")
    guilds = get_user_admin_guilds(user_id=user.get("id"))
    return render_template("server_select.html", guilds=guilds)

@app.route('/config/<guild_id>', methods=["GET", "POST"])
def config_guild(guild_id):
    user = session.get("user", None)
    if not user:
        return redirect(url_for("index"))

    guilds = get_user_admin_guilds(user_id=user.get("id"))
    if not any(str(g['id']) == guild_id for g in guilds):
        return "Keine Berechtigung für diesen Server", 403

    roles = get_guild_roles(guild_id)
    channels = get_guild_channels(guild_id)

    r = requests.get(
        f'https://dcbot-cr1m.onrender.com/guild/{guild_id}/data/load',
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    data = {}
    if r.status_code == 200:
        data = r.json().get('data', {})

    if request.method == "POST":
        form_data = request.form.to_dict()
        form_data['upload-notifications'] = {'yt': form_data.pop('upload_notify_yt', '')}
        r = requests.patch(
            f'https://dcbot-cr1m.onrender.com/guild/{guild_id}/data/update',
            headers={"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"},
            json=form_data
        )
        if r.status_code == 200:
            return redirect(url_for("index"))
        else:
            return render_template("guild_config.html", guild_id=guild_id, roles=roles, channels=channels, data=form_data), 500

    return render_template("guild_config.html", guild_id=guild_id, roles=roles, channels=channels, data=data)

@app.route('/guild/<int:guild_id>/tournaments', methods=['GET'])
def tournaments(guild_id):
    user = session.get("user", None)
    if not user:
        return redirect(url_for("index"))

    guilds = get_user_admin_guilds(user_id=user.get("id"))
    if not any(str(g['id']) == str(guild_id) for g in guilds):
        return "Keine Berechtigung für diesen Server", 403

    r = requests.get(f'https://dcbot-cr1m.onrender.com/guild/{guild_id}/tournaments')
    if r.status_code != 200:
        return r.text, r.status_code
    tournaments = r.json()
    return render_template("tournament.html", tournaments=tournaments, guild_id=guild_id)

@app.route('/guild/<int:guild_id>/tournaments/new', methods=['GET'])
def new_tournament(guild_id):
    user = session.get("user", None)
    if not user:
        return redirect(url_for("index"))

    guilds = get_user_admin_guilds(user_id=user.get("id"))
    if not any(str(g['id']) == str(guild_id) for g in guilds):
        return "Keine Berechtigung für diesen Server", 403

    r = requests.get(f'https://dcbot-cr1m.onrender.com/guild/{guild_id}/tournaments/new')
    if r.status_code != 201:
        return r.text, r.status_code

    tournament = r.json()
    tournament_id = tournament['id']
    return redirect(url_for("edit_tournament", tournament_id=tournament_id))

@app.route('/tournaments/<string:tournament_id>/edit', methods=['GET', 'POST'])
def edit_tournament(tournament_id):
    user = session.get("user", None)
    if not user:
        return redirect(url_for("index"))

    # Turnierdaten abrufen
    r = requests.get(f'https://dcbot-cr1m.onrender.com/tournaments/{tournament_id}/load')
    if r.status_code != 200:
        return "Fehler beim Abrufen der Turnierdaten", 500
    tournament = r.json()
    guild_id = tournament['guild_id']

    # Berechtigungscheck
    guilds = get_user_admin_guilds(user_id=user.get("id"))
    if not any(str(g['id']) == str(guild_id) for g in guilds):
        return "Keine Berechtigung für diesen Server", 403

    if request.method == "GET":
        return render_template("edit_tournament.html", tournament=tournament)
    elif request.method == "POST":
        data = request.form.to_dict()
        r = requests.patch(
            f'https://dcbot-cr1m.onrender.com/tournaments/{tournament_id}/update',
            headers={"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"},
            json=data
        )
        if r.status_code != 200:
            return r.text, r.status_code
        return redirect(url_for("index"))

@app.route('/tournaments/<string:tournament_id>/delete', methods=['POST', 'DELETE'])
def delete_tournament(tournament_id):
    user = session.get("user", None)
    if not user:
        return redirect(url_for("index"))

    # Turnierdaten abrufen, um guild_id zu prüfen
    r = requests.delete(
        f'https://dcbot-cr1m.onrender.com/tournaments/{tournament_id}/delete',
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    if r.status_code != 200:
        return r.text, r.status_code
    tournament = r.json()
    guild_id = tournament['guild_id']

    # Berechtigungscheck
    guilds = get_user_admin_guilds(user_id=user.get("id"))
    if not any(str(g['id']) == str(guild_id) for g in guilds):
        return "Keine Berechtigung für diesen Server", 403

    # Turnier löschen mit Auth-Header
    r = requests.get(
        f'https://dcbot-cr1m.onrender.com/tournaments/{tournament_id}/delete',
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    if r.status_code != 200:
        return r.text, r.status_code

    # Weiterleitung nach Löschung
    return redirect(url_for('tournaments', guild_id=guild_id))


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
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
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

# -----------------------------
# App starten
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
