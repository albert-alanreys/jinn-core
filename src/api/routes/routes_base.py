from flask import render_template

import config


def register_base_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html', api_url=config.API_URL)

    @app.route('/mode')
    def get_mode():
        return app.mode.value