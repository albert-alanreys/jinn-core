from flask import render_template

import config


def register_base_routes(app):
    @app.route('/')
    def index():
        return render_template(
            template_name_or_list='index.html',
            api_url=config.API_URL,
            mode=config.MODE.value
        )