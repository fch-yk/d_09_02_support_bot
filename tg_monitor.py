import logging
import textwrap

import telegram


class TelegramLogsHandler(logging.Handler):
    def __init__(self, logs_bot_token, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = telegram.Bot(token=logs_bot_token)
        self.setFormatter(
            logging.Formatter(
                fmt=(
                    '%(process)d %(levelname)s %(message)s %(asctime)s'
                    '  %(pathname)s %(funcName)s'
                )
            )
        )

    def emit(self, record):

        log_entry = self.format(record)
        max_tg_message_size = 4096
        msg_texts = textwrap.wrap(log_entry, max_tg_message_size)
        for msg_text in msg_texts:
            self.tg_bot.send_message(chat_id=self.chat_id, text=msg_text)
