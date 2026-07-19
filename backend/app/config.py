import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with validation"""
    APP_NAME = os.getenv('APP_NAME', 'AI Chatbot Assistant')
    APP_ENV = os.getenv('APP_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database/chatbot.db')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
    OPENAI_SYSTEM_PROMPT = os.getenv('OPENAI_SYSTEM_PROMPT',
                                       'You are a helpful, professional AI assistant. '
                                       'Provide clear, accurate, and concise responses.')

    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    RATE_LIMIT_CHAT = os.getenv('RATE_LIMIT_CHAT', '20 per minute')

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000')
    BASE_URL = os.getenv('BASE_URL', f'http://{HOST}:{PORT}')

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append('OPENAI_API_KEY')
        if cls.APP_ENV == 'production' and cls.SECRET_KEY == 'change-me-in-production':
            missing.append('SECRET_KEY')
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        return True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    RATE_LIMIT_DEFAULT = '60 per hour'
    RATE_LIMIT_CHAT = '10 per minute'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    OPENAI_API_KEY = 'test-key'


