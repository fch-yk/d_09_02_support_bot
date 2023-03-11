import langid


def get_language_code(text):
    langid.set_languages(['en', 'ru'])
    return langid.classify(text)[0]
