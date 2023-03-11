import json
import logging
from typing import List

from environs import Env
from google.cloud import dialogflow
from google.cloud.dialogflow_v2.types.intent import Intent

logger = logging.getLogger(__file__)


def create_intent(
        project_id: str,
        display_name: str,
        training_phrases_parts: List,
        message_texts: List,
        language_code: str
) -> Intent:
    """
    Create an intent of the given intent type.
    The sample is here:
    https://cloud.google.com/dialogflow/es/docs/how/manage-intents#create_intent
    """

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    return intents_client.create_intent(
        parent=parent,
        intent=intent,
        language_code=language_code
    )


def main():
    env = Env()
    env.read_env()
    logging.basicConfig()
    logger.setLevel(
        logging.DEBUG if env.bool("DEBUG_MODE", False) else logging.INFO
    )
    dialogflow_project_id = env.str('DIALOGFLOW_PROJECT_ID')
    questions_file_path = env.str('QUESTIONS_FILE_PATH')
    with open(questions_file_path, 'r', encoding='UTF-8') as file:
        intents_templates = json.load(file)

    for intent_display_name, intent_card in intents_templates.items():
        intent = create_intent(
            project_id=dialogflow_project_id,
            display_name=intent_display_name,
            training_phrases_parts=intent_card['questions'],
            message_texts=[intent_card['answer'], ],
            language_code=intent_card['language_code']
        )
        logger.debug('Intent created: %s', intent)


if __name__ == '__main__':
    main()
