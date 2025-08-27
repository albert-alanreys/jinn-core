from __future__ import annotations
from functools import wraps
from json import dumps
from logging import getLogger
from typing import Any, Callable

from flask import Response


logger = getLogger(__name__)


def handle_alert_api_errors(f: Callable) -> Callable:
    """
    Decorator for handling errors in alert API endpoints.
    
    Returns JSON responses with error details for:
    - KeyError: Alert not found (404)
    - TypeError/ValueError: Invalid request (400)
    - Exception: All other errors (500)
    """
    
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Response:
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            logger.exception('Alert not found')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'alert_not_found',
                    'message': f"Alert {kwargs['alert_id']} not found"
                }),
                mimetype='application/json',
                status=404
            )
        except (TypeError, ValueError) as e:
            logger.exception('Invalid request')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_request',
                    'message': str(e) or 'Invalid request parameters'
                }),
                mimetype='application/json',
                status=400
            )
        except Exception as e:
            logger.exception('Server error')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'server_error',
                    'message': 'Internal server error'
                }),
                mimetype='application/json',
                status=500
            )
    return wrapper