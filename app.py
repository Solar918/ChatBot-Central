import os
from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, flash
from dotenv import load_dotenv
from openai import OpenAI
import click

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)

# Configure app from environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Define system prompts for each chatbot (override via .env or keep defaults)
SYSTEM_PROMPTS = {
    "chatbot1": os.getenv("CHATBOT1_SYSTEM", "You are ChatBot 1, an AI assistant specialized in general knowledge."),
    "chatbot2": os.getenv("CHATBOT2_SYSTEM", "You are ChatBot 2, an AI assistant specialized in tech support."),
    "chatbot3": os.getenv("CHATBOT3_SYSTEM", "You are ChatBot 3, an AI assistant specialized in travel advice."),
    "chatbot4": os.getenv("CHATBOT4_SYSTEM", "You are ChatBot 4, an AI assistant specialized in cooking recipes."),
}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.cli.command("create-user")
@click.argument("username")
@click.argument("password")
def create_user(username, password):
    """Create a new user."""
    db.create_all()
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"Created user {username}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/chat/<bot_name>")
@login_required
def chatbot(bot_name):
    if bot_name not in SYSTEM_PROMPTS:
        abort(404)
    return render_template(f"{bot_name}.html")

@app.route("/api/chat/<bot_name>", methods=["POST"])
@login_required
def api_chat(bot_name):
    if bot_name not in SYSTEM_PROMPTS:
        return jsonify(error="Unknown chatbot"), 404
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify(error="Empty message"), 400

    api_key = os.getenv(bot_name.upper())
    if not api_key:
        return jsonify(error=f"API key for {bot_name} not set"), 500
    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[bot_name]},
                {"role": "user", "content": user_message},
            ],
        )
        answer = resp.choices[0].message.content
        return jsonify(answer=answer)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Login unsuccessful. Please check credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8005)))
