from logging import getLogger
from os import getenv

from src.infrastructure.transport import HttpClient


class TelegramClient(HttpClient):
    """
    Client for sending messages and alerts via Telegram API.
    """

    def __init__(self) -> None:
        """
        Initializes Telegram client with credentials
        from environment variables.
        
        Reads the following environment variables:
        - TELEGRAM_BOT_TOKEN: Authentication token for Telegram Bot API
        - TELEGRAM_CHAT_ID: Target chat/channel ID for sending messages
        
        Initializes:
        - token: Stores the Telegram bot token
        - chat: Stores the target chat ID
        - logger: Configured logger instance
        """

        self.token = getenv('TELEGRAM_BOT_TOKEN')
        self.chat = getenv('TELEGRAM_CHAT_ID')

        self.logger = getLogger(__name__)

    def send_order_alert(self, alert: dict) -> None:
        """
        Send formatted order alert message to Telegram.
        
        Constructs a rich HTML-formatted message from the alert dictionary
        and sends it via Telegram API.
        
        Args:
            alert: Dictionary containing order details including:
                - exchange: Exchange name
                - type: Order type
                - status: Order status
                - side: Buy/sell side
                - symbol: Trading symbol
                - qty: Order quantity
                - price: Order price
                - time: Time of the order
        """

        try:
            msg = (
                f"📊 <b>Order Information</b>\n"
                f"════════════════════\n"
                f"│ Exchange: <b>{alert['exchange']}</b>\n"
                f"│ Type: <b>{alert['type']}</b>\n"
                f"│ Status: <b>{alert['status']}</b>\n"
                f"│ Side: <b>{alert['side']}</b>\n"
                f"│ Symbol: <code>#{alert['symbol']}</code>\n"
                f"│ Quantity: <b>{alert['qty']}</b>\n"
                f"│ Price: <b>{alert['price']}</b>\n"
                f"════════════════════\n"
                f"🕒 {alert['time']}"
            )
            self.send_message(msg)
        except Exception as e:
            self.logger.error(f'{type(e).__name__}: {str(e)}')

    def send_message(self, msg: str) -> None:
        """
        Send raw message to Telegram chat.
        
        Args:
            msg: Message text to send (supports HTML formatting)
        """

        params = {
            'chat_id': self.chat,
            'text': msg,
            'parse_mode': 'HTML'
        }
        self.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            json=params,
            logging=False
        )