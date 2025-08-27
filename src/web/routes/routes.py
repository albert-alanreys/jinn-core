from __future__ import annotations
from typing import TYPE_CHECKING

from .alerts import alerts_bp
from .chart import chart_bp
from .core import core_bp
from .data import data_bp
from .execution import execution_bp
from .optimization import optimization_bp
from .report import report_bp

if TYPE_CHECKING:
    from flask import Flask


def register_routes(app: Flask) -> None:
    """
    Register all application route blueprints.
    
    Args:
        app: Flask application instance to register blueprints with.
    """

    blueprints = (
        alerts_bp,
        chart_bp,
        core_bp,
        data_bp,
        execution_bp,
        optimization_bp,
        report_bp,
    )
    
    for bp in blueprints:
        app.register_blueprint(bp)