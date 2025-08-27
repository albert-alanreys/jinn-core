from __future__ import annotations
from json import dumps

from flask import Blueprint, Response, request

from src.features.execution import execution_service
from ..errors.alerts import handle_alert_api_errors


alerts_bp = Blueprint('alerts_api', __name__, url_prefix='/api/alerts')


@alerts_bp.route('', methods=['GET'])
@handle_alert_api_errors
def get_alerts() -> Response:
    """
    Get active strategy alerts with optional filtering.
    
    Query params:
        limit: Maximum number of alerts to return (default: all)
        since_id: Return alerts created after this ID
    
    Returns: JSON response with alerts (alert_id -> alert_data)
    """

    limit = request.args.get('limit', type=int)
    since_id = request.args.get('since_id')
    alerts = execution_service.alerts
    
    if since_id is not None:
        alerts_list = list(alerts.items())

        try:
            index = next(
                i for i, (id_, _) 
                in enumerate(alerts_list) 
                if id_ == since_id
            )
            alerts = dict(alerts_list[index + 1:])
        except StopIteration:
            pass
    
    if limit and limit > 0:
        alerts = dict(list(alerts.items())[-limit:])
    
    return Response(
        response=dumps(alerts),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('/<string:alert_id>', methods=['DELETE'])
@handle_alert_api_errors
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