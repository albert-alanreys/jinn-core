from functools import wraps
from json import dumps
from typing import Callable, Any

import flask


def handle_api_errors(f: Callable) -> Callable:
    """
    Decorator for handling errors in Flask API endpoints.
    Returns JSON responses in a frontend-friendly format.

    Handles:
    - KeyError: Context not found (404) or invalid data structure (400)
    - TypeError: Data type mismatch (400)
    - ValueError: Invalid request (400)
    - Exception: All other errors (500)

    Example error response:
    {
        "status": "error",
        "type": "error_type",
        "message": "Human-readable error description"
    }

    Args:
        f (Callable): Flask route function to wrap

    Returns:
        Callable: Wrapped function with error handling
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> flask.Response:
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            if (
                'context_id' in kwargs and
                kwargs['context_id'] not in
                flask.current_app.strategy_contexts
            ):
                return flask.Response(
                    dumps({
                        'status': 'error',
                        'type': 'context_not_found',
                        'message': (
                            f'Strategy context {kwargs["context_id"]} '
                            'not found'
                        )
                    }),
                    mimetype='application/json',
                    status=404
                )
            
            if (
                'alert_id' in kwargs and
                kwargs['alert_id'] not in
                flask.current_app.strategy_alerts
            ):
                return flask.Response(
                    dumps({
                        'status': 'error',
                        'type': 'alert_not_found',
                        'message': f'Alert {kwargs["alert_id"]} not found'
                    }),
                    mimetype='application/json',
                    status=404
                )

            return flask.Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_data_structure',
                    'message': 'Required data is missing or malformed'
                }),
                mimetype='application/json',
                status=400
            )
        except TypeError as e:
            return flask.Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_type',
                    'message': str(e) or 'Data type mismatch'
                }),
                mimetype='application/json',
                status=400
            )
        except ValueError as e:
            return flask.Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_request',
                    'message': str(e) or 'Invalid request parameters'
                }),
                mimetype='application/json',
                status=400
            )
        except Exception as e:
            return flask.Response(
                dumps({
                    'status': 'error',
                    'type': 'server_error',
                    'message': str(e) or 'Internal server error'
                }),
                mimetype='application/json',
                status=500
            )

    return wrapper