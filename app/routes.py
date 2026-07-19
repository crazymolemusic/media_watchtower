from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import uuid
import os
from app.engine import load_local_vault, save_local_vault, run_infrastructure_poll

web_app = Flask(__name__, template_folder="templates")
web_app.secret_key = "WATCHTOWER_INTERNAL_LOCAL_KEY"

def encrypt_pass(password, salt=None):
    if not salt: salt = uuid.uuid4().hex
    return f"{salt}${hashlib.sha256(password.encode() + salt.encode()).hexdigest()}"

def check_pass(stored, checked):
    try:
        salt, hashed = stored.split("$")
        return hashlib.sha256(checked.encode() + salt.encode()).hexdigest() == hashed
    except Exception: return False

@web_app.route("/")
@web_app.route("/dashboard")
def dashboard():
    vault = load_local_vault()
    if not vault.get("is_installed"): return redirect(url_for("install"))
    if "user" not in session: return redirect(url_for("login"))
    return render_template("layout.html", config=vault, view="dash")

@web_app.route("/install", methods=["GET", "POST"])
def install():
    vault = load_local_vault()
    if vault.get("is_installed"): return redirect(url_for("login"))
    
    if request.method == "POST":
        p = request.form.get("password")
        if len(p) < 8 or not any(c.isdigit() for c in p):
            return "<h3>Security Policy Refused: Password requires at least 8 characters and 1 standard numeral.</h3><a href='/install'>Try Again</a>"
            
        vault["users"][request.form.get("username").strip()] = {
            "password": encrypt_pass(p), "role": "Admin", "pfp": request.form.get("pfp").strip()
        }
        vault["custom_logo_url"] = request.form.get("logo").strip()
        vault["is_installed"] = True
        save_local_vault(vault)
        return redirect(url_for("login"))
        
    return render_template("layout.html", config=vault, view="install", path=os.path.abspath("config.json"))

@web_app.route("/login", methods=["GET", "POST"])
def login():
    vault = load_local_vault()
    if request.method == "POST":
        u = request.form.get("username").strip()
        p = request.form.get("password")
        if u in vault["users"] and check_pass(vault["users"][u]["password"], p):
            session["user"] = u
            session["role"] = vault["users"][u]["role"]
            session["pfp"] = vault["users"][u]["pfp"]
            return redirect(url_for("dashboard"))
    return render_template("layout.html", config=vault, view="login")

@web_app.route("/preferences", methods=["GET", "POST"])
def preferences():
    vault = load_local_vault()
    if "user" not in session or session.get("role") != "Admin": return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        if "new_username" in request.form:
            nu = request.form.get("new_username").strip()
            np = request.form.get("new_password")
            nr = request.form.get("new_role", "User")
            if nu and np:
                vault["users"][nu] = {"password": encrypt_pass(np), "role": nr, "pfp": ""}
        else:
            vault["custom_logo_url"] = request.form.get("logo").strip()
            vault["apps"]["Pihole"]["enabled"] = "pihole_on" in request.form
            vault["apps"]["Pihole"]["url"] = request.form.get("pihole_url").strip()
            
        save_local_vault(vault)
        return redirect(url_for("preferences"))
        
    return render_template("layout.html", config=vault, view="prefs")

@web_app.route("/test-trigger")
def test_trigger():
    run_infrastructure_poll()
    return redirect(url_for("dashboard"))

@web_app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
