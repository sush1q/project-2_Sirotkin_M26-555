from . import decorators


class DBError(Exception):
    pass

class TableExistsError(DBError):
    def __init__(self, table_name):
        self.table_name = table_name
    def __str__(self):
        return f'Ошибка: Таблица "{self.table_name}" уже существует.'

class TableNotExistsError(DBError):
    def __init__(self, table_name):
        self.table_name = table_name
    def __str__(self):
        return f'Ошибка: Таблица "{self.table_name}" не существует.'

class TableArgumentsError(DBError):
    def __init__(self, args):
        self.args = args
    def __str__(self):
        return f'Ошибка: Указаны некорректные типы для параметров "{self.args}".'

ALLOWED_TYPES = ["str", "bool", "int"]

def create_table(metadata:dict, table_name: str, columns: list):
    """
    Она должна принимать текущие метаданные, имя таблицы и список столбцов.
    Автоматически добавлять столбец ID:int в начало списка столбцов.
    Проверять, не существует ли уже таблица с таким именем. Если да, выводить ошибку.
    Проверять корректность типов данных (только int, str, bool).
    В случае успеха, обновлять словарь metadata и возвращать его.
    !!! В случае, если столбец ID(уникальный ключ) не задается пользователем, то генерировать его самостоятельно.
    """
    if metadata.get(table_name) is not None:
        raise TableExistsError(table_name)
    inner_columns = columns.copy()
    
    id_column = "ID:int"
    if inner_columns.count(id_column):
        inner_columns.remove(id_column)
    inner_columns.insert(0, id_column)
    
    table_data = dict({column.split(":")[0]: column.split(":")[1]  for column in inner_columns})
    type_errors = [{k:v} for k,v in table_data.items() if v not in ALLOWED_TYPES]
    if type_errors:
        raise TableArgumentsError(type_errors)
    
    upd_metadata = metadata.copy()
    upd_metadata[table_name] = table_data
    return upd_metadata

@decorators.confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str):
    """
    Проверяет существование таблицы. Если таблицы нет, выводит ошибку.
    Удаляет информацию о таблице из metadata и возвращает обновленный словарь.
    """
    if metadata.get(table_name) is None:
        raise TableNotExistsError(table_name)
    upd_metadata = metadata.copy()
    upd_metadata.pop(table_name)
    return upd_metadata

def insert(metadata:dict, table_name:str, table_data:list, values:list):
    """
    Проверяет, существует ли таблица.
    Проверяет, что количество переданных значений соответствует количеству столбцов (минус ID).
    Валидирует типы данных для каждого значения в соответствии со схемой в metadata.
    Генерирует новый ID (например, max(IDs) + 1 или len(data) + 1).
    Добавляет новую запись (в виде словаря) в данные таблицы и возвращает их.
    """
    if table_name not in metadata:
        raise TableNotExistsError(table_name)
    table_header = metadata[table_name]
    table_header.pop("ID")
    
    if len(values) != len(table_header):
        raise ValueError("Передано неверное количество значений")
    
    new_data = {}
    new_data['ID'] = max([i['ID'] for i in table_data]) + 1
    for i, item in enumerate(table_header.items()):
        column_name, column_type = item
        column_value = values[i]
        
        if column_type == 'bool':
            if column_value.lower() not in ["true", "false"]:
                raise ValueError("Передано значение неподходящего типа")
            new_data[column_name] = bool(column_value)
        
        if column_type == 'int':
            try:
                new_data[column_name] = int(column_value)
            except:
                raise ValueError("Передано значение неподходящего типа")
        if column_type == 'str':
            if column_value[0] != '"' or column_value[-1] != '"':
                raise ValueError("Передано значение неподходящего типа")
            new_data[column_name] = column_value[1:-1]
    
    table_data.append(new_data)
    return table_data

def select(table_data:list, where_clause:dict=None):
    """
    Если where_clause не задан, возвращает все данные.
    Если задан (например, {'age': 28}), фильтрует и возвращает только подходящие записи.
    """
    if where_clause is None or where_clause == {}:
        return table_data
    return [row for row in table_data if all([row.get(k) == v for k,v in where_clause.items()])]

def update(table_data:list, set_clause:dict, where_clause:dict):
    """
    Находит записи по where_clause.
    Обновляет в найденных записях поля согласно set_clause.
    Возвращает измененные данные.
    """
    data_to_update = select(table_data, where_clause)
    upd_table_data = table_data.copy()

    for row in upd_table_data:
        if row not in data_to_update:
            continue
        for k, v in set_clause.items():
            if type(row[k]) != type(v):
                raise ValueError("Переданный тип не соответсвует типу колонки таблицы")
        row.update(set_clause)

    return upd_table_data

@decorators.confirm_action("удаление записи")
def delete(table_data:list, where_clause:dict):
    """
    Находит записи по where_clause и удаляет их.
    Возвращает измененные данные.
    """
    data_to_delete = select(table_data, where_clause)
    return [i for i in table_data if i not in data_to_delete]
