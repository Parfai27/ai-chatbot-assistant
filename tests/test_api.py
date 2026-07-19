import pytest
from unittest.mock import patch
from app import create_app
from app.services.database_service import DatabaseService
from app.services.openai_service import OpenAIService
from app.core.exceptions import ValidationError, ServiceError


class TestConfig:
    APP_NAME = 'AI Chatbot Assistant'
    APP_ENV = 'testing'
    SECRET_KEY = 'test-secret'
    DEBUG = True
    TESTING = True
    HOST = '127.0.0.1'
    PORT = 5000
    LOG_LEVEL = 'INFO'
    DATABASE_URL = 'sqlite:///:memory:'
    OPENAI_API_KEY = 'sk-test-key'
    OPENAI_MODEL = 'gpt-4o-mini'
    OPENAI_TEMPERATURE = 0.7
    OPENAI_MAX_TOKENS = 2000
    OPENAI_SYSTEM_PROMPT = 'You are a helpful assistant.'
    RATE_LIMIT_DEFAULT = '1000 per hour'
    RATE_LIMIT_CHAT = '20 per minute'
    CORS_ORIGINS = '*'
    BASE_URL = 'http://localhost.localdomain:5000'
    PREFERRED_URL_SCHEME = 'http'
    SESSION_COOKIE_SECURE = False
    SERVER_NAME = 'localhost.localdomain'


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_service(app):
    return app.extensions['db_service']


class TestHealthEndpoint:
    def test_health_returns_healthy(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_health_includes_app_info(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['app'] == 'AI Chatbot Assistant'
        assert data['env'] == 'testing'
        assert 'stats' in data


class TestSessionsEndpoint:
    def test_list_sessions_empty(self, client):
        response = client.get('/api/sessions')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['sessions']) == 0

    def test_list_sessions_limit_offset(self, client):
        response = client.get('/api/sessions?limit=10&offset=0')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['sessions']) == 0


class TestHistoryEndpoint:
    def test_history_returns_404_when_session_missing(self, client):
        response = client.get('/api/history/missing-session')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False

    def test_history_returns_paginated_messages(self, client, db_service):
        session_id = db_service.create_session(user_id='user-1')
        db_service.add_message(session_id, 'user', 'Hello')
        db_service.add_message(session_id, 'assistant', 'Hi')
        db_service.add_message(session_id, 'user', 'How are you?')
        db_service.add_message(session_id, 'assistant', 'I am fine.')

        response = client.get(f'/api/history/{session_id}?limit=2&offset=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['messages']) == 2
        assert data['messages'][0]['content'] == 'Hi'
        assert data['total'] == 4
        assert data['limit'] == 2
        assert data['offset'] == 1

    def test_history_delete_returns_empty(self, client, db_service):
        session_id = db_service.create_session(user_id='user-1')
        db_service.add_message(session_id, 'user', 'Hello')
        response = client.delete(f'/api/history/{session_id}')
        assert response.status_code == 200

        response = client.get(f'/api/history/{session_id}')
        assert response.status_code == 404


class TestChatEndpoint:
    def test_missing_message_returns_400(self, client):
        response = client.post('/api/chat', json={})
        assert response.status_code == 400

    def test_empty_message_returns_400(self, client):
        response = client.post('/api/chat', json={'message': '   '})
        assert response.status_code == 400

    @patch('app.services.openai_service.OpenAIService.chat', return_value='Mocked response')
    def test_valid_chat_returns_success(self, mock_chat, client, db_service):
        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['response'] == 'Mocked response'
        mock_chat.assert_called_once()

    @patch('app.services.openai_service.OpenAIService.chat', return_value='Mocked response')
    def test_chat_creates_session_when_missing(self, mock_chat, client, db_service):
        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'session_id' in data
        mock_chat.assert_called_once()


class TestChatEndpointValidation:
    def test_chat_rejects_non_json_payload(self, client):
        response = client.post('/api/chat', data='not-json', content_type='application/json')
        assert response.status_code == 400

    def test_chat_rejects_long_message(self, client):
        long_message = 'a' * 5001
        response = client.post('/api/chat', json={'message': long_message})
        assert response.status_code == 400


class TestServiceResilience:
    @patch('app.services.openai_service.OpenAIService.chat', side_effect=ServiceError('Provider down'))
    def test_chat_surfaces_service_error_status(self, mock_chat, client):
        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code in [502, 500, 503]
        data = response.get_json()
        assert data['success'] is False

    @patch('app.services.openai_service.OpenAIService.chat', return_value='FAQ answer')
    def test_chat_sends_faq_context_when_faq_matches_provided(self, mock_chat, client):
        response = client.post('/api/chat', json={
            'message': 'Tell me about pricing.',
            'faq_matches': ['Pricing: Starter, Growth, Enterprise']
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['response'] == 'FAQ answer'
        mock_chat.assert_called_once()
        _, kwargs = mock_chat.call_args
        assert 'faq_context' in kwargs or len(mock_chat.call_args[0]) == 3

    def test_history_limit_offset_bounds(self, client, db_service):
        session_id = db_service.create_session(user_id='user-1')
        db_service.add_message(session_id, 'user', 'Hello')
        db_service.add_message(session_id, 'assistant', 'Hi')

        response = client.get(f'/api/history/{session_id}?limit=200&offset=0')
        assert response.status_code == 200
        data = response.get_json()
        assert data['limit'] == 200
        assert len(data['messages']) == 2

        response = client.get(f'/api/history/{session_id}?limit=abc')
        assert response.status_code == 400