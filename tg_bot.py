
import functools
import html
import json
import logging
import textwrap
import traceback

from environs import Env
from telegram import ParseMode, Update, Bot
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from detect_intent import detect_intent_texts
from language_tools import get_language_code

logger = logging.getLogger(__file__)


def handle_tg_error(
    update: Update,
    context: CallbackContext,
    service_admin_tg_id: str,
    logs_bot: Bot
) -> None:
    logger.error(
        msg="Support bot: exception while handling an update:",
        exc_info=context.error
    )

    traceback_messages = traceback.format_exception(
        None,
        context.error,
        context.error.__traceback__
    )
    traceback_message = ''.join(traceback_messages)
    bot_info = html.escape(str(context.bot.get_me()))
    update_info = update.to_dict() if isinstance(update, Update)\
        else str(update)
    update_info = html.escape(
        json.dumps(update_info, indent=2, ensure_ascii=False)
    )
    chat_info = html.escape(str(context.chat_data))
    user_info = html.escape(str(context.user_data))
    message = (
        f'<pre>context.bot = {bot_info}</pre>\n\n'
        '<pre>An exception was raised while handling an update\n</pre>'
        f'<pre> update={update_info}</pre>\n\n'
        f'<pre>context.chat_data = {chat_info}</pre>\n\n'
        f'<pre>context.user_data = {user_info}</pre>\n\n'
        f'<pre>{html.escape(traceback_message)}</pre>'
    )

    max_tg_message_size = 4096
    msg_texts = textwrap.wrap(message, max_tg_message_size)
    for msg_text in msg_texts:
        logs_bot.send_message(
            chat_id=service_admin_tg_id,
            text=msg_text,
            parse_mode=ParseMode.HTML
        )


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Здравствуйте! Чем можем помочь?')


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
    logger.setLevel(
        logging.DEBUG if env.bool("DEBUG_MODE", False) else logging.INFO
    )

    updater = Updater(support_bot_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    reply_handler = functools.partial(
        reply,
        project_id=google_cloud_project,
    )
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, reply_handler))

    error_handler = functools.partial(
        handle_tg_error,
        service_admin_tg_id=env('SERVICE_ADMIN_TG_ID'),
        logs_bot=Bot(token=env('LOGS_BOT_TOKEN'))
    )
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
