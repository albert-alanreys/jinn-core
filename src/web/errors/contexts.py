from __future__ import annotations
from functools import wraps
from json import dumps
from logging import getLogger
from typing import Callable, Any

from flask import Response, current_app


logger = getLogger(__name__)


def handle_context_api_errors(f: Callable) -> Callable:
    """
    Decorator for handling errors in Flask API endpoints
    that work with strategy contexts.

    Returns JSON responses in a frontend-friendly format.

    Handles:
    - KeyError: Context not found (404) or invalid data structure (400)
    - TypeError: Data type mismatch in request parameters (400)
    - ValueError: Invalid request parameters (400)
    - Exception: All other unhandled errors (500)

    Example error response:
    {
        "status": "error",
        "type": "context_not_found",
        "message": "Context <context_id> not found"
    }

    Args:
        f: Flask route function to wrap

    Returns:
        Callable: Wrapped function with context-specific error handling
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Response:
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            logger.exception('An error occurred')

            if (
                'context_id' in kwargs and
                kwargs['context_id'] not in current_app.strategy_contexts
            ):
                return Response(
                    dumps({
                        'status': 'error',
                        'type': 'context_not_found',
                        'message': f'Context {kwargs["context_id"]} not found'
                    }),
                    mimetype='application/json',
                    status=404
                )

            return Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_data_structure',
                    'message': 'Required data is missing or malformed'
                }),
                mimetype='application/json',
                status=400
            )
        except TypeError as e:
            logger.exception('An error occurred')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_type',
                    'message': str(e) or 'Data type mismatch'
                }),
                mimetype='application/json',
                status=400
            )
        except ValueError as e:
            logger.exception('An error occurred')
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
            logger.exception('An error occurred')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'server_error',
                    'message': str(e) or 'Internal server error'
                }),
                mimetype='application/json',
                status=500
            )
    return wrapper