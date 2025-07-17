from typing import TYPE_CHECKING

from .core import core_bp
from .alerts import alerts_bp
from .chart import chart_bp
from .contexts import contexts_bp
from .report import report_bp

if TYPE_CHECKING:
    from flask import Flask


def register_routes(app: 'Flask') -> None:
    """
    Register all application routes.
    
    Args:
        app: Flask application instance
    """

    app.register_blueprint(core_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(contexts_bp)
    app.register_blueprint(chart_bp)
    app.register_blueprint(report_bp)