from waitress import serve

from src.web import create_app


if __name__ == '__main__':
    app = create_app()
    serve(app, host='127.0.0.1', port=app.config['PORT'])