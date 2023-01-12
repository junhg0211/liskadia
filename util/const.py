from json import load
from os import listdir
from os.path import join

with open('res/string.json', 'r', encoding='utf-8') as file:
    _string = load(file)
with open('res/secret.json', 'r', encoding='utf-8') as file:
    _secret = load(file)
with open('res/languages.json', 'r', encoding='utf-8') as file:
    _language_meta = load(file)

_languages = dict()
for filename in listdir('res/language'):
    if filename.endswith('.json'):
        with open(join('res', 'language', filename), 'r', encoding='utf-8') as file:
            _languages[filename[:-5]] = load(file)

DEFAULT_LANGUAGE = 'en-US'


def parse(dictionary: dict, directory: str):
    directory = directory.split('.')
    while directory:
        dictionary = dictionary[directory.pop(0)]
    return dictionary


def get_string(directory: str):
    return parse(_string, directory)


def get_secret(directory: str):
    return parse(_secret, directory)


def get_language(directory: str, language: str):
    language = _languages[language]
    try:
        return parse(language, directory)
    except KeyError:
        return f'{{{directory}}}'


def get_language_list_html(selected_language: str = DEFAULT_LANGUAGE):
    result = list()
    for code, name in _language_meta['name'].items():
        selected = ' selected' if selected_language == code else ''
        result.append(f'<option value="{code}"{selected}>{name}</option>')
    result = '\n'.join(result)
    return result


def is_valid_language(string: str):
    return string in _languages
