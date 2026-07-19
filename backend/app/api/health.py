from flask import Blueprint, jsonify, current_app
from app.services.database_service import DatabaseService

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        db_service: DatabaseService = current_app.extensions.get('db_service')
        stats = db_service.get_stats() if db_service else {"service_ready": False}

        return jsonify({
            "status": "healthy",
            "app": "AI Chatbot Assistant",
            "env": current_app.config['APP_ENV'],
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503
