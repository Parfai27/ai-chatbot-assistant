# AI Chatbot Assistant

AI Chatbot Assistant is a polished full-stack chatbot application built with Flask, OpenAI, SQLAlchemy, and a lightweight frontend. It provides a practical foundation for conversational AI experiences, persistent chat history, and RESTful integrations that can be extended for demos, internal tools, or production pilots.

## Overview

This project combines a modular backend, a responsive web interface, and container-friendly deployment into a single, maintainable application. It is designed to be easy to run locally while still providing a professional structure for future growth.

## Key features

- OpenAI-powered conversational responses
- Persistent chat sessions and message history with SQLite
- Session-based interaction flow for multi-turn conversations
- REST API endpoints for chat, history, sessions, and health checks
- Responsive frontend served directly by the Flask application
- Docker-based deployment support and CI workflow integration

## Technology stack

- Backend: Python 3.11, Flask, SQLAlchemy
- AI integration: OpenAI API
- Frontend: HTML, CSS, JavaScript
- Data: SQLite
- DevOps: Docker Compose, GitHub Actions

## Project structure

```text
ai-chatbot-assistant/
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── services/
│       └── utils/
├── frontend/
├── docs/
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Getting started

### Prerequisites

- Python 3.11+
- pip
- An OpenAI API key

### Installation

```bash
git clone <your-repo-url>
cd ai-chatbot-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update the values in `.env`, especially `OPENAI_API_KEY`.

### Initialize the database

```bash
python scripts/init_db.py
```

### Run the application

```bash
cd backend
python run.py
```

Then open your browser at `http://localhost:5000/`.

## Configuration

The application reads configuration from environment variables defined in `.env`. Important settings include:

- `OPENAI_API_KEY`: required for AI responses
- `APP_ENV`: set to `development` or `production`
- `SECRET_KEY`: required in production
- `DATABASE_URL`: defaults to the local SQLite database

## API overview

The project exposes a small REST API for interacting with the application. Detailed documentation is available in [docs/api.md](docs/api.md).

Common endpoints include:

- `GET /api/health`
- `GET /api/sessions`
- `POST /api/chat`
- `GET /api/history/<session_id>`
- `DELETE /api/history/<session_id>`

## Testing and quality

Run the test suite with:

```bash
python scripts/run_tests.py
```

## Deployment

The application can be run locally or in containers.

### Docker Compose

```bash
docker compose up --build
```

### Docker

```bash
docker build -t ai-chatbot-assistant .
docker run -p 5000:5000 --env-file .env ai-chatbot-assistant
```

## Documentation

- [docs/api.md](docs/api.md)
- [docs/architecture.md](docs/architecture.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the MIT License.
