from .routes_base import register_base_routes
from .routes_data import api_bp


def register_routes(app):
    register_base_routes(app)
    app.register_blueprint(api_bp)