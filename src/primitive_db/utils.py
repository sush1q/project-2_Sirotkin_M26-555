import json
import os
from . import constants


def load_metadata(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(json.dumps(data))

def load_table_data(table_name):
    table_data = load_metadata(os.path.join(constants.DATA_DIR, f"{table_name}.json"))
    return table_data if table_data else []

def save_table_data(table_name, data):
    os.makedirs(constants.DATA_DIR, exist_ok=True)
    save_metadata(os.path.join(constants.DATA_DIR, f"{table_name}.json"), data)

def delete_table(table_name):
    filepath = os.path.join(constants.DATA_DIR, f"{table_name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
