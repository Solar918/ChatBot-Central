import os
from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv
import openai

load_dotenv()
app = Flask(__name__)

# Define system prompts for each chatbot (override via .env or keep defaults)
SYSTEM_PROMPTS = {
    "chatbot1": os.getenv("CHATBOT1_SYSTEM", "You are ChatBot 1, an AI assistant specialized in general knowledge."),
    "chatbot2": os.getenv("CHATBOT2_SYSTEM", "You are ChatBot 2, an AI assistant specialized in tech support."),
    "chatbot3": os.getenv("CHATBOT3_SYSTEM", "You are ChatBot 3, an AI assistant specialized in travel advice."),
    "chatbot4": os.getenv("CHATBOT4_SYSTEM", "You are ChatBot 4, an AI assistant specialized in cooking recipes."),
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/chat/<bot_name>")
def chatbot(bot_name):
    if bot_name not in SYSTEM_PROMPTS:
        abort(404)
    return render_template(f"{bot_name}.html")

@app.route("/api/chat/<bot_name>", methods=["POST"])
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
    openai.api_key = api_key
    try:
        resp = openai.ChatCompletion.create(
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8005)))
