import logging
import random

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkEventType, VkLongPoll
from detect_intent import detect_intent_texts

logger = logging.getLogger(__file__)


def reply(user_id, vk_api, input_text, project_id):
    intent_texts = detect_intent_texts(
        project_id=project_id,
        session_id=user_id,
        texts=[input_text],
        language_code="ru-Ru",
    )
    if intent_texts['is_fallback']:
        logger.debug('fallback <-- %s', input_text)
        return
    vk_api.messages.send(
        user_id=user_id,
        message=intent_texts['conversation_items'][0]['fulfillment_text'],
        random_id=random.randint(1, 1000)
    )


def main() -> None:
    env = Env()
    env.read_env()
    vk_group_token = env.str('VK_GROUP_TOKEN')
    dialogflow_project_id = env.str('DIALOGFLOW_PROJECT_ID')
    logging.basicConfig()
    logger.setLevel(
        logging.DEBUG if env.bool("DEBUG_MODE", False) else logging.INFO
    )
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reply(event.user_id, vk_api, event.text, dialogflow_project_id)


if __name__ == '__main__':
    main()
