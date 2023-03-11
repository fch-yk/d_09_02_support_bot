
import logging
import functools


from environs import Env
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from detect_intent import detect_intent_texts
from tg_monitor import TelegramLogsHandler
from language_tools import get_language_code

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


def reply(
    update: Update,
    context: CallbackContext,
    project_id: str,
) -> None:
    message_text = ''
    try:
        message = update.message
        message_text = message.text
        intent_texts = detect_intent_texts(
            project_id=project_id,
            session_id=message.chat_id,
            texts=[message_text],
            language_code=get_language_code(message_text),
        )
        message.reply_text(
            intent_texts['conversation_items'][0]['fulfillment_text']
        )
    except Exception as error:
        logger.error('Reply to "%s" failed: %s ', message_text, error)


def main() -> None:
    env = Env()
    env.read_env()
    support_bot_token = env('SUPPORT_BOT_TOKEN')
    google_cloud_project = env.str('GOOGLE_CLOUD_PROJECT')

    logging.basicConfig()
    logs_handler = TelegramLogsHandler(
        logs_bot_token=env('LOGS_BOT_TOKEN'),
        chat_id=env('SERVICE_ADMIN_TG_ID'),
    )

    logger.addHandler(logs_handler)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(
        logging.DEBUG if env.bool("DEBUG_MODE", False) else logging.INFO
    )

    updater = Updater(support_bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    reply_handler = functools.partial(
        reply,
        project_id=google_cloud_project,
    )
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, reply_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
