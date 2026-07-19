from flask import Blueprint, send_from_directory
import os

frontend_bp = Blueprint('frontend', __name__)

frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'frontend')


@frontend_bp.route('/')
def index():
    return send_from_directory(frontend_dir, 'index.html')


@frontend_bp.route('/static/<path:path>')
def serve_static(path):
    static_dir = os.path.join(frontend_dir, 'static')
    target = os.path.join(static_dir, path)
    if os.path.exists(target):
        return send_from_directory(static_dir, path)
    return 'Not Found', 404


def init_frontend(app):
    app.register_blueprint(frontend_bp)
