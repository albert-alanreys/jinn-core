import os

from flask import Flask
from flask_cors import CORS

from src.api.handlers import StrategyUpdateHandler
from src.api.routes import register_routes
from src.core.enums import Mode


def create_app(
    import_name: str,
    static_folder: str,
    template_folder: str,
    strategy_contexts: dict,
    mode: Mode
) -> Flask:
    """
    Creates and configures a Flask application instance with necessary
    routes, CORS settings, and strategy context integration.

    Depending on the mode, it may also launch a background handler
    to monitor and process strategy updates.

    Args:
        import_name (str): Name of the application package
        static_folder (str): Path to the folder with static files
        template_folder (str): Path to the folder with HTML templates
        strategy_contexts (dict): Dictionary mapping strategy IDs
                                  to their contexts
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
    app.updated_contexts = []
    app.strategy_alerts = {}
    app.new_alerts = {}

    if mode is Mode.AUTOMATION:
        handler = StrategyUpdateHandler(strategy_contexts, app)
        handler.start()

    return app