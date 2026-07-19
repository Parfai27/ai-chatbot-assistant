from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure database parent directory exists for the default SQLite URL
    default_db_url = 'sqlite:///database/chatbot.db'
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(backend_dir, 'database', 'chatbot.db')
    if app.config.get('DATABASE_URL', default_db_url) == default_db_url:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
