# ChatBot Central

ChatBot Central is a Flask-based web application that hosts multiple GPT-powered chatbots,
each with customizable system prompts and live token-by-token streaming responses.

## Features
- Multi-bot interface (ChatBot 1–4) with per-bot GPT model configuration.
- Live streaming of assistant replies via newline-delimited JSON chunks.
- Override system prompts via environment variables, code defaults, or external prompt files.
- Containerized deployment with Docker for easy setup.

## Prerequisites
- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- OpenAI API key(s)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/ChatBot-Central.git
cd ChatBot-Central
```

### 2. Python Setup
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file and edit your settings:
   ```bash
   cp example.env .env
   ```
4. In `.env`, set your OpenAI API keys and Flask config:
   ```dotenv
   # OpenAI API keys for each chatbot (replace with real keys)
   CHATBOT1=sk-...
   CHATBOT2=sk-...
   CHATBOT3=sk-...
   CHATBOT4=sk-...

   # Optional: override default system prompts
   # CHATBOT1_SYSTEM="Your custom prompt here"

   # Flask configuration
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///site.db
   ```
5. (Optional) If using openai-python v1.x, pin or migrate:
   ```bash
   pip install openai==0.28.0
   ```
6. Start the Flask application:
   ```bash
   flask run --host=0.0.0.0 --port=8005
   ```
7. Open your browser at `http://localhost:8005/login` to authenticate and access the chatbots.

### 3. Docker Setup
Build and run in a container (reads `.env` automatically):
```bash
# Build the Docker image
docker build -t chatbot-central .

# Run the container
docker run -d \
  --name chatbot-central \
  --env-file .env \
  -p 8005:8005 \
  chatbot-central
```
Then visit `http://localhost:8005/login` in your browser.

## Configuration

### GPT Model Configuration
Modify `model_config.json` to change the model and reasoning level used by each chatbot:
```json
{
  "chatbot1": { "model": "gpt-5-nano", "reasoning": "minimal" },
  "chatbot2": { "model": "gpt-5-nano", "reasoning": "minimal" },
  "chatbot3": { "model": "gpt-5-nano", "reasoning": "minimal" },
  "chatbot4": { "model": "gpt-5-nano", "reasoning": "minimal" }
}
```
You can set the optional `reasoning` field to control reasoning depth (`minimal`, `medium`, `detailed`), with `minimal` as the default for faster responses.
Supported values include any OpenAI chat-capable model (e.g. `gpt-4`, `gpt-3.5-turbo`).

### Custom System Prompts
System prompts are loaded in priority order:

1. **Prompt files** (default) — edit `prompts/<bot_name>.txt` (e.g. `prompts/chatbot1.txt`) to set each chatbot’s system message.
2. **Environment overrides** (optional) — for quick tests, set `CHATBOT<N>_SYSTEM` in `.env`:
   ```dotenv
   CHATBOT1_SYSTEM="You are an expert math tutor."
   ```
3. **Code defaults** (fallback) — edit the `SYSTEM_PROMPTS` dictionary in `app.py` if no file or env override is provided:
   ```python
   SYSTEM_PROMPTS = {
       "chatbot1": os.getenv("CHATBOT1_SYSTEM", "You are ChatBot 1, an AI assistant…"),
       # …
   }
   ```

## Streaming Responses
The `/api/chat/<bot_name>` endpoint streams delta tokens as newline-delimited JSON.
The client-side script in `static/chatbotscript.js` reads each chunk and appends `content` to the chat bubble in real time.

## Project Structure
```
├── app.py                # Flask application and API routes
├── model_config.json     # Per-bot GPT model settings
├── example.env           # Template for .env configuration
├── requirements.txt      # Python dependencies
├── prompts/              # Optional system prompt files
├── static/               # Front-end assets (CSS, JS, images)
├── templates/            # Jinja2 HTML templates for chat UI
└── Dockerfile            # Containerization instructions
```

## Renaming Chatbot Pages

The chatbot templates are loaded dynamically via Flask's route in `app.py`:

```python
@app.route('/templates/<template_name>.html')
@login_required
def serve_template(template_name):
    valid = ['chatbot1', 'chatbot2', 'chatbot3', 'chatbot4', 'contact']
    if template_name not in valid:
        abort(404)
    return render_template(f"{template_name}.html")
```

To rename a chatbot page (for example, from `chatbot1.html` to `historybot.html`):
1. Rename the file in the `templates/` directory: `templates/historybot.html`.
2. Update the `valid` list in the `serve_template` function above to include the new name:

   ```diff
   - valid = ['chatbot1', 'chatbot2', 'chatbot3', 'chatbot4', 'contact']
   + valid = ['historybot', 'chatbot2', 'chatbot3', 'chatbot4', 'contact']
   ```

3. Update the navigation links in your templates (`base.html`, `index.html`, `contact.html`) to point to `templates/historybot.html` instead of `templates/chatbot1.html`.
4. (Optional) If you have custom model or system prompts keyed by `chatbot1`, update the keys in `model_config.json` and the `SYSTEM_PROMPTS` dictionary in `app.py` to use `historybot`.

After making these changes, restart the Flask application and navigate to `/templates/historybot.html`.

## Troubleshooting
- Check your browser console for streaming parse errors (`Stream parse error:`).
- Verify `.env` keys are correct and loaded (`CHATBOT<N>` must match case in `app.py`).
- Ensure your OpenAI API quota is available and keys are valid.

## Development
To auto-reload templates and disable static file caching during development, enable Flask debug mode:
```bash
export FLASK_ENV=development
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8005
```

## License
This project is licensed under the MIT License. See `LICENSE` for details.
The application also automatically adjusts `max_completion_tokens` based on reasoning:
- `minimal`: 100 tokens
- `medium`: 300 tokens
- `detailed`: 600 tokens
