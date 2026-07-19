# API Documentation

Base path: `/api`

Authentication: None in this sample. Add token/session auth in production.

## Health

`GET /api/health`

Response:
```json
{
  "status": "healthy",
  "app": "AI Chatbot Assistant",
  "env": "production",
  "stats": {
    "total_sessions": 1,
    "total_messages": 2,
    "active_sessions": 1
  }
}
```

Errors:
- `503` when the database service is unavailable.

## Chat

`POST /api/chat`

Request body:
```json
{
  "message": "What is machine learning?",
  "session_id": "optional-existing-session-id",
  "user_id": "optional-user-id",
  "faq_matches": ["Title: body", "Title: body"]
}
```

Response:
```json
{
  "success": true,
  "session_id": "new-or-existing-session-id",
  "response": "Machine learning is ...",
  "is_faq_match": true,
  "message_count": 2
}
```

Errors:
- `400` for missing/empty message
- `401` for unauthorized when auth is enabled
- `422` for invalid payload shape
- `429` when rate-limited
- `500` for unexpected backend errors

## History

`GET /api/history/<session_id>?limit=50&offset=0`

Response:
```json
{
  "success": true,
  "session_id": "session-id",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hello",
      "timestamp": "2026-07-19T12:34:56Z",
      "tokens_used": null,
      "is_faq_match": false
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

Errors:
- `404` when the session does not exist
- `400` when `limit` is not an integer

`DELETE /api/history/<session_id>`

Response:
```json
{
  "success": true,
  "message": "Session closed and history cleared"
}
```

Errors:
- `404` when the session does not exist

Pagination rules:
- `limit` is capped at `200`
- `offset` defaults to `0`

## Sessions

`GET /api/sessions?limit=50&offset=0&user_id=optional-user-id`

Response:
```json
{
  "success": true,
  "sessions": [
    {
      "id": "session-id",
      "user_id": "user-1",
      "created_at": "2026-07-19T12:00:00Z",
      "updated_at": "2026-07-19T12:34:56Z",
      "message_count": 2
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

Errors:
- `503` when the database service is unavailable

Notes:
- Only active sessions are returned
- Results are ordered by `updated_at` descending
