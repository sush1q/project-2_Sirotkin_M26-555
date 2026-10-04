import json
from pathlib import Path

DATA_DIR = Path("data")

def load_metadata(filepath):
    try:
        with open(filepath, "r") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    with open(filepath, "w") as file:
        file.write(json.dumps(data))

def load_table_data(table_name):
    table_data = load_metadata(f"{DATA_DIR}/{table_name}.json")
    return table_data if table_data else []

def save_table_data(table_name, data):
    save_metadata(f"{DATA_DIR}/{table_name}.json", data)
