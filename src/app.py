import logging
import threading

from dotenv import load_dotenv

from src.core.strategies.utils import load_strategies
from src.features.automation.service import AutomationService
from src.web.server import create_app


class AppInitializer:
    def start(self):
        self._load_strategies()

        print(self.strategies)

    def _load_strategies(self):
        self.strategies = load_strategies()




# def init_strategies():
#     return load_strategies()

# def init_services(strategies):
#     automation_service = AutomationService(strategies)
#     threading.Thread(target=automation_service.run, daemon=True).start()
#     return automation_service

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