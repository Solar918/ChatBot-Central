# ChatBot Central Setup Guide

This guide explains how to configure API keys and customize system prompts for each chatbot.

## 0. Environment Configuration

In your `.env` file, set the Flask secret key and database URL:

```dotenv
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///site.db
```

If you’re using openai-python v1.x, update your code via `openai migrate` or pin the library to v0.28.x:

```bash
pip install openai==0.28.0
```

## 1. Adding API Keys

1. **Create a `.env` file** in your project root (if you haven’t already).
2. **Define each chatbot’s key** using uppercase names matching `app.py`’s config. For example:
   ```dotenv
   CHATBOT1=sk-yourkey1…
   CHATBOT2=sk-yourkey2…
   CHATBOT3=sk-yourkey3…
   CHATBOT4=sk-yourkey4…
   ```
3. **Install and load** `python-dotenv` (already in `requirements.txt`) so the app picks up `.env` automatically.
4. **Restart your Flask server**; the keys are read at startup and used by the `/api/chat/<bot_name>` endpoint.

## 2. Customizing System Instructions

| Approach                | Location                           | Notes                                                        |
|-------------------------|------------------------------------|--------------------------------------------------------------|
| **Environment Override**| `.env`                             | Add `CHATBOT1_SYSTEM="Your custom prompt here"` entries.    |
| **Code Defaults**       | In `app.py` → `SYSTEM_PROMPTS` dict | Edit the default strings if you prefer hard‑coded prompts.    |

```python
SYSTEM_PROMPTS = {
    "chatbot1": os.getenv(
        "CHATBOT1_SYSTEM",
        "You are ChatBot 1, an AI assistant specialized in general knowledge."
    ),
    # …
}
```

## 3. Using Separate Prompt Files (Optional)

For richer, versioned prompts, store each system message in its own file:

1. **Create a `prompts/` folder** at project root.
2. **Add files** like `prompts/chatbot1.txt`, `prompts/chatbot2.txt`, etc., containing your system messages.
3. **Load them** in `app.py`:
   ```python
   def load_prompt(name):
       with open(f"prompts/{name}.txt") as f:
           return f.read().strip()

   SYSTEM_PROMPTS = {
       bot: load_prompt(bot)
       for bot in ["chatbot1","chatbot2","chatbot3","chatbot4"]
   }
   ```
4. **Reload** the server to apply the changes.

## Summary
- **API keys:** Set `CHATBOT<N>=…` entries in `.env`.
- **System prompts:** Override via `.env` or edit `SYSTEM_PROMPTS` in `app.py`.
- **Advanced prompts:** Place prompt files in `prompts/` and load dynamically.

Feel free to review and let me know if you’d like any adjustments!

## Docker Deployment

Build the Docker image and run the container with your `.env`:
```bash
# Build the image
docker build -t chatbot-central .

# Run the container (reads env vars from .env and maps port 8005)
docker run -d \
  --name chatbot-central \
  --env-file .env \
  -p 8005:8005 \
  chatbot-central
```

Then visit `http://localhost:8005/login` to sign in and access the chatbots.
## Streaming responses

The `/api/chat/<bot_name>` endpoint now streams tokens as they arrive, and the client-side JS appends each token to the chat bubble in real time.
