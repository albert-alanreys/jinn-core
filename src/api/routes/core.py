from os import getenv

import flask


core_bp = flask.Blueprint('core', __name__)


@core_bp.route('/', methods=['GET'])
def index() -> str:
    """
    Serve main frontend application page.
    
    Returns:
        Rendered HTML template with initial configuration.
    """

    return flask.render_template(
        template_name_or_list='index.html',
        server_url=getenv('SERVER_URL', 'http://127.0.0.1:5000'),
        server_mode=flask.current_app.mode.value
    )