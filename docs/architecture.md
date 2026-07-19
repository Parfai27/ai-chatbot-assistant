# Architecture Overview

This project is organized as a small full-stack application with a Flask backend and a browser-based frontend.

## High-level structure

- Backend: Flask application, REST API, service layer, and persistence
- Frontend: static HTML, CSS, and JavaScript served by the Flask app
- Data layer: SQLite through SQLAlchemy models and database services
- DevOps: Docker Compose for local/container deployment and GitHub Actions for CI

## Backend modules

- backend/app/api: route handlers for health, chat, history, sessions, and frontend delivery
- backend/app/core: shared prompt logic, exceptions, and application-level helpers
- backend/app/models: SQLAlchemy database models for sessions and messages
- backend/app/services: OpenAI and database integrations
- backend/app/utils: logging and validation helpers

## Request flow

1. A request enters the Flask app through the appropriate API blueprints.
2. The route handler validates the request and calls the relevant service layer.
3. The service layer interacts with the database and the OpenAI client.
4. The response is returned as JSON for the API routes, or HTML/CSS/JS for the frontend routes.

## Extending the app

- Add new endpoints in backend/app/api.
- Put reusable logic in backend/app/services or backend/app/core.
- Keep UI changes in frontend/static and frontend/index.html.
- Update documentation under docs/ when API behavior changes.
