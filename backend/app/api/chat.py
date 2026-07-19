from flask import Blueprint, request, jsonify, current_app
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService
from app.utils.validators import validate_chat_request, sanitize_text
from app.core.exceptions import ValidationError, ServiceError
import logging

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for AI conversation"""
    try:
        data = request.get_json(silent=True)
        validate_chat_request(data)

        message = sanitize_text(str(data.get('message', '')))
        session_id = str(data.get('session_id', '')).strip() or None
        user_id = data.get('user_id')
        faq_matches = data.get('faq_matches')

        openai_service = current_app.extensions['openai_service']
        db_service = current_app.extensions['db_service']

        current_session_id = session_id or db_service.get_or_create_session(user_id=user_id)

        history = db_service.get_history(current_session_id)
        faq_context = '\n'.join(faq_matches) if faq_matches else None

        ai_response = openai_service.chat(message, history, faq_context)

        db_service.add_message(
            session_id=current_session_id,
            role='user',
            content=message,
        )
        db_service.add_message(
            session_id=current_session_id,
            role='assistant',
            content=ai_response,
            is_faq_match=bool(faq_context),
        )

        logger.info(
            f"Chat processed: session={current_session_id} "
            f"message_len={len(message)} response_len={len(ai_response)}"
        )

        return jsonify({
            "success": True,
            "session_id": current_session_id,
            "response": ai_response,
            "is_faq_match": bool(faq_context),
            "message_count": len(history) + 2,
        })

    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return jsonify({"success": False, "error": e.message}), e.status_code
    except ServiceError as e:
        logger.error(f"Service error: {e.message}")
        return jsonify({"success": False, "error": e.message}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500
