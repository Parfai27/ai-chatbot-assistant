from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import os
from dotenv import load_dotenv

load_dotenv()

from app.config import Config
from app.api.chat import chat_bp
from app.api.history import history_bp
from app.api.health import health_bp
from app.api.frontend import init_frontend
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService


def _get_root_dirs():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return base, os.path.join(base, 'frontend'), os.path.join(base, 'frontend', 'static')


def _normalize_config(app):
    test_mode = app.config.get('TESTING', False)
    if test_mode:
        app.config.setdefault('SERVER_NAME', 'localhost.localdomain')
        app.config.setdefault('SESSION_COOKIE_SECURE', False)
        app.config.setdefault('PREFERRED_URL_SCHEME', 'http')


def create_app(config_class=Config):
    root_dir, frontend_dir, static_dir = _get_root_dirs()

    app = Flask(
        __name__,
        static_folder=static_dir,
        static_url_path='/static',
        template_folder=frontend_dir,
    )

    app.config.from_object(config_class)
    _normalize_config(app)

    # Enable security headers only in production.
    # Dev/test should never force HTTPS redirects.
    if app.config.get('APP_ENV') == 'production':
        Talisman(app)
    else:
        Talisman(app, force_https=False)

    CORS(app, origins=app.config['CORS_ORIGINS'].split(','))

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config['RATE_LIMIT_DEFAULT']],
        storage_uri='memory://'
    )
    app.extensions['limiter'] = limiter

    openai_service = OpenAIService(config_class)
    db_service = DatabaseService(config_class.DATABASE_URL)
    app.extensions['openai_service'] = openai_service
    app.extensions['db_service'] = db_service

    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    init_frontend(app)

    return app
