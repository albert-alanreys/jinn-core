import flask

from src.api.utils.network import get_server_url


core_bp = flask.Blueprint('core', __name__)


@core_bp.route('/', methods=['GET'])
def index() -> str:
    """
    Serve main frontend application page.
    
    Returns:
        Rendered HTML template with initial configuration
    """

    server_url = get_server_url()
    return flask.render_template(
        template_name_or_list='index.html',
        server_url=server_url,
        server_mode=flask.current_app.mode.value
    )