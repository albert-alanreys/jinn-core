from json import dumps

from flask import Blueprint, Response, current_app

from src.api.errors.alerts import handle_alert_api_errors


alerts_bp = Blueprint('alerts_api', __name__, url_prefix='/api/alerts')


@alerts_bp.route('', methods=['GET'])
@handle_alert_api_errors
def get_all_alerts(limit: int = None) -> Response:
    """
    Get all active strategy alerts.

    Query Parameters:
        limit (int, optional): Maximum number of recent alerts to return.
                               If not provided, returns all alerts

    Returns:
        Response: JSON response containing dictionary
                  of active alerts (id -> alert)
    """

    alerts = current_app.strategy_alerts
    
    if limit is not None and limit > 0:
        alerts = dict(list(alerts.items())[-limit:])
    
    return Response(
        response=dumps(alerts),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('/since/<string:last_alert_id>', methods=['GET'])
@handle_alert_api_errors
def get_alerts_since(last_alert_id: str) -> Response:
    """
    Get all alerts that were created after the specified alert ID.

    Args:
        last_alert_id (str): The ID of the last alert the client has received.
                             Returns all alerts if the ID is not found.

    Returns:
        Response: JSON response containing dictionary
                  of new alerts {id: alert}
    """
    alerts = current_app.strategy_alerts
    alerts_list = list(alerts.items())
    
    try:
        index = next(
            i for i, (id_, _) 
            in enumerate(alerts_list) 
            if id_ == last_alert_id
        )
        new_alerts = dict(alerts_list[index + 1:])
    except StopIteration:
        new_alerts = alerts.copy()
    
    return Response(
        response=dumps(new_alerts),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('/<string:alert_id>', methods=['DELETE'])
@handle_alert_api_errors
def delete_alert(alert_id: str) -> Response:
    """
    Remove alert from active alerts collection.

    Args:
        alert_id (str): Unique identifier of the alert

    Returns:
        Response: JSON response with operation status
    """

    current_app.strategy_alerts.pop(alert_id)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )