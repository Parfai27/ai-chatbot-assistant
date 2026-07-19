from app.core.exceptions import ValidationError


def validate_chat_request(data):
    """Validate incoming chat request payload"""
    if not data:
        raise ValidationError("Request body is required")
    if 'message' not in data or not str(data['message']).strip():
        raise ValidationError("Message field is required and must not be empty")
    if len(data['message']) > 4000:
        raise ValidationError("Message exceeds maximum length of 4000 characters")
    if 'session_id' in data and len(str(data['session_id'])) > 100:
        raise ValidationError("Session ID is too long")
    if 'user_id' in data and len(str(data['user_id'])) > 100:
        raise ValidationError("User ID is too long")
    return True


def sanitize_text(text):
    """Basic input sanitization for XSS prevention"""
    if not isinstance(text, str):
        return ''
    dangerous_tags = ['<script', '</script>', '<iframe', '</iframe>', 'javascript:', 'onerror=']
    sanitized = text
    for tag in dangerous_tags:
        sanitized = sanitized.replace(tag, '')
    return sanitized.strip()
