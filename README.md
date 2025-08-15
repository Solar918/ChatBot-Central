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
Modify `model_config.json` to change the model used by each chatbot:
```json
{
  "chatbot1": "gpt-5-nano",
  "chatbot2": "gpt-5-nano",
  "chatbot3": "gpt-5-nano",
  "chatbot4": "gpt-5-nano"
}
```
Supported values include any OpenAI chat-capable model (e.g. `gpt-4`, `gpt-3.5-turbo`).

### Custom System Prompts
You can steer each bot’s behavior by customizing its system prompt:

1. **Environment Overrides** (recommended for quick tweaks)
   - In your `.env`, set `CHATBOT<N>_SYSTEM`:
     ```dotenv
     CHATBOT1_SYSTEM="You are an expert math tutor."
     ```

2. **Code Defaults**
   - Edit the `SYSTEM_PROMPTS` dictionary in `app.py` to change hard-coded defaults:
     ```python
     SYSTEM_PROMPTS = {
         "chatbot1": os.getenv("CHATBOT1_SYSTEM", "You are ChatBot 1…"),
         # …
     }
     ```

3. **External Prompt Files**
   - Place or edit plain-text files in `prompts/` (e.g. `prompts/chatbot1.txt`).
   - By default, the application reads each system prompt from `prompts/<bot_name>.txt`; modify those files to customize your chatbots.

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

## Troubleshooting
- Check your browser console for streaming parse errors (`Stream parse error:`).
- Verify `.env` keys are correct and loaded (`CHATBOT<N>` must match case in `app.py`).
- Ensure your OpenAI API quota is available and keys are valid.

## License
This project is licensed under the MIT License. See `LICENSE` for details.
