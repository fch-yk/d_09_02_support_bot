from environs import Env
from google.cloud import dialogflow


def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)
    conversation_items = []

    for text in texts:
        text_input = dialogflow.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        query_result = session_client.detect_intent(
            request={"session": session_path, "query_input": query_input}
        ).query_result

        conversation_items.append(
            {
                'query_text': query_result.query_text,
                'detected_intent': query_result.intent.display_name,
                'confidence': query_result.intent_detection_confidence,
                'fulfillment_text': query_result.fulfillment_text,
            }
        )

    return {
        'session_path': session_path,
        'conversation_items': conversation_items,
        'is_fallback': query_result.intent.is_fallback,
    }


def main() -> None:
    env = Env()
    env.read_env()
    user_id = env.str('TELEGRAM_USER_ID')
    dialogflow_project_id = env.str('DIALOGFLOW_PROJECT_ID')
    texts = [
        'Кто здесь?',
        'Хеллоу',
        'приветствую',
        'и что?'
    ]

    conversation_report = detect_intent_texts(
        project_id=dialogflow_project_id,
        session_id=user_id,
        texts=texts,
        language_code='ru-Ru'
    )

    print('session path: ', conversation_report['session_path'])
    for item in conversation_report['conversation_items']:
        print("=" * 20)
        print('query text:', item['query_text'])
        print('detected_intent:', item['detected_intent'])
        print('confidence:', item['confidence'])
        print('fulfillment text:', item['fulfillment_text'])


if __name__ == '__main__':
    main()
