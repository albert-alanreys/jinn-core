from os import getenv

from flask import render_template


def register_base_routes(app):
    @app.route('/', methods=['GET'])
    def index():
        return render_template(
            template_name_or_list='index.html',
            api_url=getenv('API_URL', 'http://127.0.0.1:5000'),
            mode=app.mode.value
        )