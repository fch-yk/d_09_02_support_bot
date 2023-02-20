
import logging

from environs import Env
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)


logger = logging.getLogger(__file__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Здравствуйте! Чем можем помочь?')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Задайте вопрос боту поддержки издательства'
        '"Игра глаголов"'
    )


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    env = Env()
    env.read_env()
    support_bot_token = env('SUPPORT_BOT_TOKEN')

    logging.basicConfig()
    logger.setLevel(
        logging.DEBUG if env.bool("DEBUG_MODE", False) else logging.INFO
    )

    updater = Updater(support_bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
