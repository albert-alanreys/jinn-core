from __future__ import annotations

from flask import Blueprint, render_template

from ..network import get_server_url


core_bp = Blueprint('core', __name__)


@core_bp.route('/', methods=['GET'])
def index() -> str:
    """
    Serve main frontend application page.
    
    Returns:
        Rendered HTML template with initial configuration
    """

    return render_template(
        template_name_or_list='index.html',
        server_url=get_server_url()
    )