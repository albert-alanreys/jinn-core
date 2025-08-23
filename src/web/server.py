from __future__ import annotations
from logging import basicConfig, INFO
from os import getenv
from os.path import abspath, join

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .routes import register_routes


def create_app() -> Flask:
    """
    Factory function to create and configure a Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """

    load_environment()
    configure_logging()
    
    app = Flask(
        __name__,
        static_folder=get_static_path(),
        template_folder=get_templates_path()
    )
    
    configure_app(app)
    setup_cors(app)
    register_routes(app)
    
    return app


def load_environment() -> None:
    """Load environment variables from .env file."""

    load_dotenv()


def configure_logging() -> None:
    """Configure basic logging settings."""

    basicConfig(
        level=INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_static_path() -> str:
    """
    Get absolute path to static files directory.
    
    Returns:
        str: Absolute path to static directory
    """
    
    return abspath(join('src', 'web', 'dist'))


def get_templates_path() -> str:
    """
    Get absolute path to templates directory.
    
    Returns:
        str: Absolute path to templates directory
    """

    return abspath(join('src', 'web', 'dist'))


def configure_app(app: Flask) -> None:
    """
    Configure application settings from environment variables.
    
    Args:
        app: Flask application instance to configure
    """

    app.config.update({
        'PORT': int(getenv('SERVER_PORT', 5000)),
        'DEBUG': getenv('FLASK_DEBUG', 'false').lower() == 'true',
        'ENV': getenv('FLASK_ENV', 'production')
    })


def setup_cors(app: Flask) -> None:
    """
    Configure Cross-Origin Resource Sharing (CORS) for the application.
    
    Args:
        app: Flask application instance to configure CORS for
    """

    cors_origins = getenv('CORS_ORIGINS', '')
    
    if cors_origins:
        origins = [origin.strip() for origin in cors_origins.split(',')]
    else:
        origins = '*'
    
    CORS(app, resources={r'/api/*': {'origins': origins}})