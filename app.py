import os
from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, flash, Response, stream_with_context, session
from dotenv import load_dotenv
from openai import OpenAI
import json
import click

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
# Automatically reload templates and disable static file caching in development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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
    "chatbot1": os.getenv("CHATBOT1_SYSTEM", "You are ChronoChat uses immersive roleplay prompting. The AI assumes the first-person voice of a historical figure, staying in character with authentic vocabulary, biases, and worldview. Modern questions are answered through the lens of the chosen persona."),
    "chatbot2": os.getenv("CHATBOT2_SYSTEM", "You are WildMind prompts GPT to fully inhabit an animal (real or mythical). It emphasises sensory-rich, non-human descriptions and encourages the user to role-play alongside. Human logic is replaced by instinct, sensation, and poetry."),
    "chatbot3": os.getenv("CHATBOT3_SYSTEM", "You are FixIt Frenzy, an AI assistant specialized in troubleshooting and problem-solving."),
    "chatbot4": os.getenv("CHATBOT4_SYSTEM", "You are GamePlan Live, an AI assistant specialized in providing real-time gaming strategies and tips."),
}
# Load per-chatbot model configuration
try:
    with open("model_config.json") as f:
        MODEL_CONFIG = json.load(f)
except FileNotFoundError:
    MODEL_CONFIG = {}


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
    # Clear previous conversation on page load
    session.pop(f"history_{bot_name}", None)
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

    # Initialize and update conversation history in session
    session_key = f"history_{bot_name}"
    history = session.get(session_key, [])
    history.append({"role": "user", "content": user_message})
    session[session_key] = history

    def generate():
        assistant_response = ""
        bot_cfg = MODEL_CONFIG.get(bot_name, {})
        model_name = bot_cfg.get("model", "gpt-3.5-turbo")
        reasoning_level = bot_cfg.get("reasoning", "minimal")
        system_prompt = f"{SYSTEM_PROMPTS[bot_name]}\n\n[Using {reasoning_level} reasoning]"
        # Adjust maximum tokens based on reasoning level for faster minimal responses
        max_tokens_map = {"minimal": 100, "medium": 300, "detailed": 600}
        max_tokens = max_tokens_map.get(reasoning_level, 100)
        try:
            for chunk in client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, *history],
                max_completion_tokens=max_tokens,
                stream=True,
            ):
                # extract streamed content from ChoiceDelta object
                delta = getattr(chunk.choices[0].delta, "content", None)
                if delta:
                    assistant_response += delta
                    yield json.dumps({"content": delta}) + "\n"
        except Exception as e:
            # Surface any API or streaming errors to the client
            yield json.dumps({"content": f"[Error: {str(e)}]"}) + "\n"
            return
        # Append assistant response to history
        history.append({"role": "assistant", "content": assistant_response})
        session[session_key] = history

    return Response(stream_with_context(generate()), mimetype="application/json")


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

@app.route('/templates/<template_name>.html')
@login_required
def serve_template(template_name):
    valid = ['chatbot1', 'chatbot2', 'chatbot3', 'chatbot4', 'contact']
    if template_name not in valid:
        abort(404)
    return render_template(f"{template_name}.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8005)))
