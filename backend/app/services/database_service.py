from typing import List, Dict, Optional
import json
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from app.models.database import Session as DBSession, Message, init_db


class DatabaseService:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = init_db(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

    def _get_session(self):
        return self.SessionLocal()

    def create_session(self, user_id: Optional[str] = None, metadata: Dict = None) -> str:
        db = self._get_session()
        try:
            session_obj = DBSession(
                user_id=user_id,
                metadata_json=json.dumps(metadata or {})
            )
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)
            return session_obj.id
        finally:
            db.close()

    def get_session(self, session_id: str) -> Optional[DBSession]:
        db = self._get_session()
        try:
            return db.query(DBSession).filter_by(id=session_id, is_active=True).first()
        finally:
            db.close()

    def get_or_create_session(self, user_id: str = None, metadata: Dict = None) -> str:
        db = self._get_session()
        try:
            existing = db.query(DBSession).filter_by(
                user_id=user_id, is_active=True
            ).order_by(DBSession.updated_at.desc()).first()

            if existing:
                existing.updated_at = datetime.now(timezone.utc)
                db.commit()
                return existing.id
        finally:
            db.close()
        return self.create_session(user_id, metadata)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens_used: int = None,
        model_used: str = None,
        is_faq_match: bool = False,
        metadata: Dict = None,
    ) -> Message:
        from datetime import datetime, timezone
        db = self._get_session()
        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                tokens_used=tokens_used,
                model_used=model_used,
                is_faq_match=is_faq_match,
                metadata_json=json.dumps(metadata or {}),
                timestamp=datetime.now(timezone.utc),
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message
        finally:
            db.close()

    def get_history(self, session_id: str, limit: int = 50, offset: int = 0) -> Dict:
        db = self._get_session()
        try:
            items = (
                db.query(Message)
                .filter_by(session_id=session_id)
                .order_by(Message.timestamp.asc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            total = db.query(Message).filter_by(session_id=session_id).count()
            return {
                "items": [
                    {
                        "id": m.id,
                        "role": m.role,
                        "content": m.content,
                        "timestamp": m.timestamp.isoformat(),
                        "tokens_used": m.tokens_used,
                        "is_faq_match": m.is_faq_match,
                    }
                    for m in items
                ],
                "total": total,
            }
        finally:
            db.close()

    def get_all_sessions(self, user_id: str = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        db = self._get_session()
        try:
            query = db.query(DBSession).filter_by(is_active=True)
            if user_id:
                query = query.filter_by(user_id=user_id)
            sessions = (
                query.order_by(DBSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            return [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "message_count": len(getattr(s, 'messages', [])),
                }
                for s in sessions
            ]
        finally:
            db.close()

    def close_session(self, session_id: str) -> bool:
        db = self._get_session()
        try:
            session_obj = db.query(DBSession).filter_by(id=session_id).first()
            if session_obj:
                session_obj.is_active = False
                db.commit()
                return True
            return False
        finally:
            db.close()

    def clear_history(self, session_id: str) -> bool:
        db = self._get_session()
        try:
            result = db.query(Message).filter_by(session_id=session_id).delete(synchronize_session=False)
            db.commit()
            return result > 0
        finally:
            db.close()

    def get_stats(self) -> Dict:
        db = self._get_session()
        try:
            return {
                "total_sessions": db.query(DBSession).count(),
                "total_messages": db.query(Message).count(),
                "active_sessions": db.query(DBSession).filter_by(is_active=True).count(),
            }
        finally:
            db.close()
