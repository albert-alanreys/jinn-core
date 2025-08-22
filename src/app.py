import logging

from dotenv import load_dotenv

from src.features.execution import executionService
# from src.web.server import create_app


class AppInitializer:
    def __init__(self) -> None:
        load_dotenv()
        logging.basicConfig(level=logging.INFO)

    def start(self):
        print(executionService)


# def init_web(strategies):
#     app = create_app(strategies)
#     return app

# def run():
#     load_dotenv()
#     logging.basicConfig(level=logging.INFO)

#     strategies = init_strategies()
#     init_services(strategies)
#     app = init_web(strategies)
#     app.run(host="0.0.0.0", port=5000)