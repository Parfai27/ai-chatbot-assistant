from flask import Blueprint, request, jsonify, current_app
from app.core.exceptions import ValidationError

history_bp = Blueprint('history', __name__)


@history_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get chat history for a session"""
    try:
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))
        db_service = current_app.extensions.get('db_service')
        if not db_service:
            return jsonify({"success": False, "error": "Service unavailable"}), 503

        session = db_service.get_session(session_id)
        if not session:
            return jsonify({"success": False, "error": "Session not found"}), 404

        history = db_service.get_history(session_id, limit=limit, offset=offset)
        return jsonify({
            "success": True,
            "session_id": session_id,
            "messages": history["items"],
            "total": history["total"],
            "limit": limit,
            "offset": offset,
        })

    except ValueError:
        return jsonify({"success": False, "error": "Invalid limit parameter"}), 400
    except Exception as e:
        current_app.extensions['logger'].error(f"History fetch error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to retrieve history"}), 500


@history_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions"""
    try:
        user_id = request.args.get('user_id')
        limit = min(int(request.args.get('limit', 50)), 100)
        db_service = current_app.extensions.get('db_service')
        if not db_service:
            return jsonify({"success": False, "error": "Service unavailable"}), 503

        sessions = db_service.get_all_sessions(user_id=user_id, limit=limit)
        return jsonify({
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        })
    except Exception as e:
        current_app.extensions['logger'].error(f"Sessions list error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to list sessions"}), 500


@history_bp.route('/history/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """Clear chat history for a session"""
    try:
        db_service = current_app.extensions.get('db_service')
        if not db_service:
            return jsonify({"success": False, "error": "Service unavailable"}), 503

        result = db_service.close_session(session_id)
        if result:
            db_service.clear_history(session_id)
            return jsonify({"success": True, "message": "Session closed and history cleared"})
        return jsonify({"success": False, "error": "Session not found"}), 404
    except Exception as e:
        current_app.extensions['logger'].error(f"History clear error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to clear history"}), 500
