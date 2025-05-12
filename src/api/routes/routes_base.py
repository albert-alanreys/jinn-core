from flask import render_template


def register_base_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/mode')
    def get_mode():
        return app.mode.value