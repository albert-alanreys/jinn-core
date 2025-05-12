from .routes_alerts import register_alert_routes
from .routes_data import register_data_routes
from .routes_base import register_base_routes


def register_routes(app):
    register_base_routes(app)
    register_alert_routes(app)
    register_data_routes(app)