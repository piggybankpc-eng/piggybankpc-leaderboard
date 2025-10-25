"""
PiggyBankPC Leaderboard - Configuration
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-CHANGE-IN-PRODUCTION'

    # Database
    BASE_DIR = Path(__file__).parent
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR}/instance/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(BASE_DIR / 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'pbr'}

    # Pagination
    SUBMISSIONS_PER_PAGE = 20

    # Security module
    BENCHMARK_SECURITY_KEY = os.environ.get('BENCHMARK_SECURITY_KEY') or 'PIGGYBANK_PC_BENCHMARK_SECRET_2025'

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"

    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['BASE_DIR'] / 'instance', exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        Config.init_app(app)

        # Validate SECRET_KEY in production
        if not app.config.get('SECRET_KEY') or app.config['SECRET_KEY'] == 'dev-secret-key-CHANGE-IN-PRODUCTION':
            raise ValueError("SECRET_KEY environment variable must be set in production!")

        # Validate BENCHMARK_SECURITY_KEY
        if not app.config.get('BENCHMARK_SECURITY_KEY'):
            raise ValueError("BENCHMARK_SECURITY_KEY environment variable must be set in production!")

        # Log startup
        import logging
        logging.info("🚀 PiggyBankPC Leaderboard starting in PRODUCTION mode")
        logging.info(f"📊 Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')[:50]}...")


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
