import os

from flask import Flask
from flask_cors import CORS

from src.api.routes import register_routes
from src.core.enums import Mode


def create_app(
    import_name: str,
    static_folder: str,
    template_folder: str,
    strategy_contexts: dict,
    strategy_alerts: dict,
    mode: Mode
) -> Flask:
    """
    Creates and configures a Flask application instance with necessary
    routes, CORS settings, and strategy context integration.

    Args:
        import_name (str): Name of the application package
        static_folder (str): Path to the folder with static files
        template_folder (str): Path to the folder with HTML templates
        strategy_contexts (dict): Dictionary of strategy contexts
        strategy_alerts (dict): Dictionary of strategy alerts
        mode (Mode): Operating mode of the application

    Returns:
        Flask: Configured Flask application instance
    """

    app = Flask(
        import_name=import_name,
        static_folder=static_folder,
        template_folder=template_folder
    )

    register_routes(app)

    cors_origins = os.getenv('CORS_ORIGINS') or '*'
    CORS(app, resources={r'/api/*': {'origins': cors_origins}})

    app.mode = mode
    app.strategy_contexts = strategy_contexts
    app.strategy_alerts = strategy_alerts

    return app