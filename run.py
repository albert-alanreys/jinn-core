from logging import getLogger

from dotenv import load_dotenv
from waitress import serve


logger = getLogger(__name__)
load_dotenv()

if __name__ == '__main__':
    from src.web import create_app

    app = create_app()

    base_url = app.config.get('BASE_URL')
    port = app.config['PORT']

    if base_url:
        logger.info(f'👉 Open: {base_url}')
    else:
        logger.info(f'👉 Open: http://127.0.0.1:{port}')

    serve(app, host='0.0.0.0', port=port)