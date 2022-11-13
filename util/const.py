from json import load

with open('res/string.json', 'r') as file:
    _string = load(file)


def parse(dictionary: dict, directory: str):
    directory = directory.split('.')
    while directory:
        dictionary = dictionary[directory.pop(0)]
    return dictionary


def get_string(directory: str):
    return parse(_string, directory)
