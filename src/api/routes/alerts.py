from json import dumps
import flask

from src.api.utils.error_handling import handle_api_errors


alerts_bp = flask.Blueprint('alerts_api', __name__, url_prefix='/api/alerts')


@alerts_bp.route('', methods=['GET'])
@handle_api_errors
def get_all_alerts():
    """
    Get all active strategy alerts.

    Query Parameters:
        limit (int, optional): Maximum number of recent alerts to return.
                               If not provided, returns all alerts.

    Returns:
        Response: JSON response containing dictionary
                  of active alerts (id -> alert).
    """

    alerts = flask.current_app.strategy_alerts
    limit = flask.request.args.get('limit', type=int)
    
    if limit is not None and limit > 0:
        alerts = dict(list(alerts.items())[-limit:])
    
    return flask.Response(
        response=dumps(alerts),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('/<string:alert_id>', methods=['DELETE'])
@handle_api_errors
def delete_alert(alert_id):
    """
    Remove alert from active alerts collection.

    Args:
        alert_id (str): Unique identifier of the alert.

    Returns:
        Response: JSON response with operation status.
    """

    flask.current_app.strategy_alerts.pop(alert_id)

    return flask.Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )


@alerts_bp.route('/new', methods=['GET'])
@handle_api_errors
def get_new_alerts():
    """
    Get new alerts that haven't been fetched yet and
    clear the new alerts buffer.
    
    Returns:
        Response: JSON response containing dictionary
                  of new alerts {id: alert}.
    """

    new_alerts = flask.current_app.new_alerts.copy()
    flask.current_app.new_alerts.clear()

    return flask.Response(
        response=dumps(new_alerts),
        status=200,
        mimetype='application/json'
    )