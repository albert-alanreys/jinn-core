from __future__ import annotations
from functools import wraps
from json import dumps
from logging import getLogger
from typing import Callable, Any

from flask import Response


logger = getLogger(__name__)


def with_context_error_handling(f: Callable) -> Callable:
    """
    Decorator for handling errors in strategy context API endpoints.
    
    Returns JSON responses with error details for:
    - KeyError: Context not found (404)
    - TypeError/ValueError: Invalid request (400)
    - Exception: All other errors (500)
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Response:
        try:
            return f(*args, **kwargs)
        except KeyError:
            logger.exception('Context not found')
            context_id = kwargs.get('context_id', 'unknown')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'context_not_found',
                    'message': f'Context {context_id} not found'
                }),
                mimetype='application/json',
                status=404
            )
        except (TypeError, ValueError):
            logger.exception('Invalid request')
            return Response(
                dumps({
                    'status': 'error',
                    'type': 'invalid_request',
                    'message': 'Invalid request parameters'
                }),
                mimetype='application/json',
                status=400
            )
        except Exception:
            logger.exception('An error occurred')
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