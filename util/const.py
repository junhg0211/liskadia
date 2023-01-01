from json import load
from os import listdir
from os.path import join

with open('res/string.json', 'r', encoding='utf-8') as file:
    _string = load(file)
with open('res/secret.json', 'r', encoding='utf-8') as file:
    _secret = load(file)

_languages = dict()
for filename in listdir('res/language'):
    if filename.endswith('.json'):
        with open(join('res', 'language', filename), 'r', encoding='utf-8') as file:
            _languages[filename[:-5]] = load(file)


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
    return parse(language, directory)


def is_valid_language(string: str):
    return string in _languages
