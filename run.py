from dotenv import load_dotenv
from waitress import serve


load_dotenv()

if __name__ == '__main__':
    from src.web import create_app

    app = create_app()
    serve(app, host='0.0.0.0', port=app.config['PORT'])