from os import getenv

from flask import render_template


def register_base_routes(app):
    @app.route('/', methods=['GET'])
    def index():
        return render_template(
            template_name_or_list='index.html',
            server_url=getenv('SERVER_URL', 'http://127.0.0.1:5000'),
            server_mode=app.mode.value
        )