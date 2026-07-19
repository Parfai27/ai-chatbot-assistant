import pytest
from app.services.database_service import DatabaseService
import uuid


@pytest.fixture
def db_service():
    return DatabaseService('sqlite:///:memory:')


class TestDatabaseService:
    def test_create_session(self, db_service):
        session_id = db_service.create_session(user_id='user-1')
        assert session_id is not None

    def test_add_message(self, db_service):
        session_id = db_service.create_session()
        msg = db_service.add_message(session_id, 'user', 'Hello')
        assert msg.content == 'Hello'
        assert msg.role == 'user'

    def test_get_history(self, db_service):
        session_id = db_service.create_session()
        db_service.add_message(session_id, 'user', 'Hello')
        db_service.add_message(session_id, 'assistant', 'Hi there')

        payload = db_service.get_history(session_id)
        assert payload['total'] >= 2
        assert payload['items'][0]['content'] == 'Hello'

    def test_get_all_sessions(self, db_service):
        db_service.create_session(user_id='user-1')
        db_service.create_session(user_id='user-2')

        sessions = db_service.get_all_sessions(user_id='user-1')
        assert any(s['user_id'] == 'user-1' for s in sessions)

    def test_close_session(self, db_service):
        session_id = db_service.create_session()
        result = db_service.close_session(session_id)
        assert result is True

    def test_clear_history(self, db_service):
        session_id = db_service.create_session()
        db_service.add_message(session_id, 'user', 'Hello')
        db_service.add_message(session_id, 'assistant', 'Hi')

        result = db_service.clear_history(session_id)
        assert result is True

    def test_get_stats(self, db_service):
        db_service.create_session()
        db_service.create_session()
        stats = db_service.get_stats()
        assert stats['total_sessions'] >= 2
