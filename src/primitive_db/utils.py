import json
import os
from . import constants


def load_metadata(filepath):
    """Загружает JSON-файл или возвращает пустой словарь, если файла нет."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(json.dumps(data))

def load_table_data(table_name):
    """Загружает записи таблицы, возвращая пустой список при отсутствии данных."""
    table_data = load_metadata(os.path.join(constants.DATA_DIR, f"{table_name}.json"))
    return table_data if table_data else []

def save_table_data(table_name, data):
    """Создаёт каталог данных при необходимости и сохраняет записи таблицы."""
    os.makedirs(constants.DATA_DIR, exist_ok=True)
    save_metadata(os.path.join(constants.DATA_DIR, f"{table_name}.json"), data)

def delete_table(table_name):
    """Удаляет файл таблицы, если он существует."""
    filepath = os.path.join(constants.DATA_DIR, f"{table_name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
