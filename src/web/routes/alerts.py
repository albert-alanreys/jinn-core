from json import dumps

from flask import Blueprint, Response, current_app, request

from ..errors.alerts import handle_alert_api_errors


alerts_bp = Blueprint('alerts_api', __name__, url_prefix='/api/alerts')


@alerts_bp.route('', methods=['GET'])
@handle_alert_api_errors
def get_alerts() -> Response:
    """
    Get active strategy alerts with optional filtering.

    Query Parameters:
        limit (int, optional): Maximum number of most recent alerts to return.
            If not specified, returns all alerts.
        since_id (str, optional): Alert identifier for filtering.
            Only alerts created after this ID will be returned.
            If ID is not found, returns all alerts.

    Returns:
        Response: JSON response containing a dictionary of alerts
                  (alert_id -> alert_data).
    """

    limit = request.args.get('limit', type=int)
    since_id = request.args.get('since_id')
    
    alerts = current_app.strategy_alerts
    
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
            alerts = alerts.copy()
    
    if limit is not None and limit > 0:
        alerts = dict(list(alerts.items())[-limit:])
    
    return Response(
        response=dumps(alerts),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('', methods=['GET'])
@handle_alert_api_errors
def get_all_alerts() -> Response:
    """
    Get all active strategy alerts.

    Query Parameters:
        limit (int, optional): Maximum number of most recent alerts to return.
            Defaults to 100 if not specified in the request.

    Returns:
        Response: JSON response containing a dictionary of active alerts
                  (alert_id -> alert_data).
    """

    limit = request.args.get('limit', default=100, type=int)
    alerts = current_app.strategy_alerts
    
    if limit > 0:
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

    current_app.strategy_alerts.pop(alert_id)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )