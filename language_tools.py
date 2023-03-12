import py3langid


def get_language_code(text):
    py3langid.set_languages(['en', 'ru'])
    return py3langid.classify(text)[0]
