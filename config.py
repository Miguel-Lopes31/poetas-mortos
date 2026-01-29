import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-biblioteca-pessoal'
    
    # Database configuration (supports both SQLite and PostgreSQL/Supabase)
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    # Fix for Supabase/Heroku: postgres:// -> postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
