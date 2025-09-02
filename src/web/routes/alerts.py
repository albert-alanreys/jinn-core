from __future__ import annotations
from json import dumps

from flask import Blueprint, Response, request

from src.features.execution import execution_service
from ..errors.alerts import with_alert_error_handling
from ..formatting.alerts import format_alerts


alerts_bp = Blueprint('alerts_api', __name__, url_prefix='/api/alerts')


@alerts_bp.route('', methods=['GET'])
@with_alert_error_handling
def get_alerts() -> Response:
    """
    Get active strategy alerts with optional filtering.
    
    Query params:
        limit: Maximum number of alerts to return (default: all)
        since_id: Return alerts created after this ID
    
    Returns: JSON response with alerts as a list of objects
    """

    limit = request.args.get('limit', type=int)
    since_id = request.args.get('since_id')
    alerts = execution_service.alerts
    
    if since_id is not None:
        try:
            index = next(
                i for i, alert in enumerate(alerts)
                if alert['alert_id'] == since_id
            )
            alerts = alerts[index + 1 :]
        except StopIteration:
            pass
    
    if limit and limit > 0:
        alerts = alerts[-limit:]

    formatted_alerts = format_alerts(alerts)
    return Response(
        response=dumps(formatted_alerts),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('/<string:alert_id>', methods=['DELETE'])
@with_alert_error_handling
def delete_alert(alert_id: str) -> Response:
    """
    Remove alert from active alerts collection.

    Path Parameters:
        alert_id: Unique identifier of the alert

    Returns:
        Response: JSON response with operation status
    """

    execution_service.delete_alert(alert_id)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )