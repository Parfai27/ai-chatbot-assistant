# AI-Powered Chatbot/Assistant

A production-grade, business-ready AI chatbot platform built with **Flask**, **OpenAI GPT-4**, **SQLite**, and a **professional-grade architecture** ready for real deployment and business use.

## Features

- Natural language understanding with **OpenAI GPT-4**
- Context-aware short-term memory per conversation
- Persistent **SQLite** chat history with session management
- **Voice input** using Web Speech API with browser-native transcription
- **FAQ keyword matching** for fast, contextual answers
- Clean, responsive **HTML/CSS/JavaScript** frontend
- Session sidebar, typing indicator, and mobile-friendly chat experience
- **Flask REST API** with rate limiting, security headers, structured logging, and pagination
- History pagination and session listing endpoints
- Error handling, validation, and monitoring out of the box
- Ready for **Docker** deployment

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11 + Flask |
| AI / LLM | OpenAI GPT-4 / GPT-4o-mini |
| Database | SQLAlchemy + SQLite |
| Frontend | HTML5 + CSS + JavaScript |
| DevOps | Docker, GitHub Actions CI |

## Project Structure

```
ai-chatbot-assistant/
  backend/
    app/
      api/         # REST endpoints
      core/        # prompts and exceptions
      models/      # SQLAlchemy models
      services/    # OpenAI + database services
      utils/       # logging and validation
      __init__.py  # Flask app factory
  frontend/
    index.html
    static/
      css/style.css
      js/app.js
  docs/
    api.md
  tests/
  docker-compose.yml
  Dockerfile
  README.md
```

## Quick Start

1. Clone the repo and enter the project directory:
```bash
git clone <your-repo-url>
cd ai-chatbot-assistant
```

2. Copy environment setup:
```bash
cp .env.example backend/.env
# Edit backend/.env with your OPENAI_API_KEY
```

3. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

5. Run the backend:
```bash
cd backend
python run.py
```

6. Open the frontend:
```bash
open frontend/index.html
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Service health and stats |
| `/api/sessions` | GET | List active sessions |
| `/api/chat` | POST | Send a chat message, optional `session_id`, `faq_matches` |
| `/api/history/<session_id>` | GET | Retrieve chat history with `limit` and `offset` |
| `/api/history/<session_id>` | DELETE | Clear a session |

### Example: Chat Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'
```

## Production Notes

- Set `APP_ENV=production`.
- Set `OPENAI_API_KEY` and `SECRET_KEY`.
- Use HTTPS in front of the app in production.
- Review rate-limit and CORS settings for your deployment domain.

## Deployment

- Build the container with `docker build -t ai-chatbot-assistant .`
- Run with `docker-compose up --build`
- Use `.env` for environment-specific settings

## Run Locally

- Activate the project virtual environment
- Start the backend with `cd backend && python run.py`
- Open the frontend at the served `/` route

Note: in some Windows shell/network environments, browser-based checks against `/` are more reliable than shell HTTP probes to the Flask dev server.

## License

MIT
