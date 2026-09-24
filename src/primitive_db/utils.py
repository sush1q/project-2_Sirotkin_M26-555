import json


def load_metadata(filepath):
    try:
        with open(filepath, "r") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    with open(filepath, "w") as file:
        file.write(json.dumps(data))
