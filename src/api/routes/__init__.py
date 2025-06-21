from typing import TYPE_CHECKING

from .routes_base import register_base_routes
from .routes_data import api_bp as data_bp
from .routes_report import report_bp

if TYPE_CHECKING:
    from flask import Flask


def register_routes(app: 'Flask') -> None:
    register_base_routes(app)

    app.register_blueprint(data_bp)
    app.register_blueprint(report_bp)