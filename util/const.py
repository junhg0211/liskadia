from json import load

with open('res/string.json', 'r', encoding='utf-8') as file:
    _string = load(file)
with open('res/secret.json', 'r', encoding='utf-8') as file:
    _secret = load(file)


def parse(dictionary: dict, directory: str):
    directory = directory.split('.')
    while directory:
        dictionary = dictionary[directory.pop(0)]
    return dictionary


def get_string(directory: str):
    return parse(_string, directory)


def get_secret(directory: str):
    return parse(_secret, directory)