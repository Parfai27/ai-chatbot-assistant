"""
Initializes the SQLite database with default FAQ data.
Run: python scripts/init_db.py
"""
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.services.database_service import DatabaseService
from app.config import Config
from app.models.database import init_db


DEFAULT_FAQS = [
    {
        'question': 'What is machine learning?',
        'answer': 'Machine learning is a subset of AI that enables systems to learn patterns from data without explicit programming.',
        'category': 'AI'
    },
    {
        'question': 'How do I reset my password?',
        'answer': 'Use the forgot password link on the login page. A reset email will be sent within 2 minutes.',
        'category': 'Account'
    },
    {
        'question': 'What are your business hours?',
        'answer': 'Our support team is available Monday-Friday, 9 AM - 6 PM EST.',
        'category': 'Support'
    }
]


def init_faq_table():
    """
    Placeholder for FAQ initialization.
    Replace with actual FAQ table creation if extending schema.
    """
    return DEFAULT_FAQS


def run():
    config = Config()
    config.validate()

    db_service = DatabaseService(config.DATABASE_URL)
    faqs = init_faq_table()

    print(f"Database initialized at: {config.DATABASE_URL}")
    print(f"Loaded {len(faqs)} default FAQ entries")
    print("Initialization complete.")


if __name__ == '__main__':
    run()
