from datetime import timedelta
import os


class Config:
    """Base configuration with sensible defaults.

    - Keep DEBUG off by default.
    - Read `SECRET_KEY` from environment; fall back to a placeholder for local dev.
    - Shared session and security-related defaults here; override in subclasses.
    """
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-for-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Session cookie settings (can be tightened in ProductionConfig)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Development configuration: local file DB, debug on, no HTTPS enforcement."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    # In development we typically don't run behind HTTPS locally
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration: read DB URL and strong cookie protections."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Ensure a real secret is provided in the environment for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# Usage examples:
# 1) In your app factory call:
#    app.config.from_object('config.DevelopmentConfig')
#    or
#    app.config.from_object('config.ProductionConfig')
#
# 2) Or make it environment-driven in your entrypoint (recommended):
#    env = os.getenv('FLASK_ENV', 'production')
#    if env == 'development':
#        app.config.from_object('config.DevelopmentConfig')
#    else:
#        app.config.from_object('config.ProductionConfig')