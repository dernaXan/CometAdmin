from flask import request
from flask import Flask, make_response
import secrets

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
    
