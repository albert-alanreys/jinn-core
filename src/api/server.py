from flask import Flask
from flask_cors import CORS

from src.core.enums import Mode
from .routes import register_routes
from .strategy_update_handler import StrategyUpdateHandler


def create_app(
    import_name: str,
    static_folder: str,
    template_folder: str,
    strategy_contexts: dict,
    mode: Mode
) -> Flask:
    app = Flask(
        import_name=import_name,
        static_folder=static_folder,
        template_folder=template_folder
    )

    register_routes(app)

    CORS(
        app,
        resources={r'/api/*': {'origins': 'http://localhost:5173'}}
    )

    app.mode = mode
    app.strategy_contexts = strategy_contexts
    app.updated_contexts = []
    app.strategy_alerts = {}
    app.new_alerts = {}

    if mode is Mode.AUTOMATION:
        handler = StrategyUpdateHandler(strategy_contexts, app)
        handler.start()

    return app