from . import decorators, constants


def get_table_header(metadata:dict, table_name:str):
    """Получить схему таблицы, если таблицы нет - вызывает исключение"""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]

def check_clause(table_header:dict, clause:dict):
    """Проверяет столбцы и типы значений условия по схеме таблицы"""
    for column_name, value in (clause or {}).items():
        if column_name not in table_header:
            raise KeyError(column_name)
        if type(value).__name__ != table_header[column_name]:
            raise ValueError(f'Неверный тип значения столбца "{column_name}"')

@decorators.handle_db_errors
def create_table(metadata:dict, table_name: str, columns: list):
    """
    Она должна принимать текущие метаданные, имя таблицы и список столбцов.
    Автоматически добавлять столбец ID:int в начало списка столбцов.
    Проверять, не существует ли уже таблица с таким именем. Если да, выводить ошибку.
    Проверять корректность типов данных (только int, str, bool).
    В случае успеха, обновлять словарь metadata и возвращать его.
    !!! В случае, если столбец ID(уникальный ключ) не задается пользователем, то генерировать его самостоятельно.
    """
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    table_data = {"ID": "int"}
    seen_columns = set()
    for column in columns:
        parts = column.split(":")
        if len(parts) != 2:
            raise ValueError(f'Некорректное описание столбца: {column}')
        column_name, column_type = parts
        if column_name in seen_columns:
            raise ValueError(f'Повторяющийся столбец: {column_name}')
        if column_type not in constants.ALLOWED_TYPES:
            raise ValueError(f'Некорректный тип столбца: {column_type}')
        if column_name == "ID" and column_type != "int":
            raise ValueError("Столбец ID должен иметь тип int")
        seen_columns.add(column_name)
        table_data[column_name] = column_type
    
    upd_metadata = metadata.copy()
    upd_metadata[table_name] = table_data
    return upd_metadata

@decorators.confirm_action("удаление таблицы")
@decorators.handle_db_errors
def drop_table(metadata: dict, table_name: str):
    """
    Проверяет существование таблицы. Если таблицы нет, выводит ошибку.
    Удаляет информацию о таблице из metadata и возвращает обновленный словарь.
    """
    get_table_header(metadata, table_name)
    upd_metadata = metadata.copy()
    upd_metadata.pop(table_name)
    return upd_metadata

@decorators.log_time
@decorators.handle_db_errors
def insert(metadata:dict, table_name:str, table_data:list, values:list):
    """
    Проверяет, существует ли таблица.
    Проверяет, что количество переданных значений соответствует количеству столбцов (минус ID).
    Валидирует типы данных для каждого значения в соответствии со схемой в metadata.
    Генерирует новый ID (например, max(IDs) + 1 или len(data) + 1).
    Добавляет новую запись (в виде словаря) в данные таблицы и возвращает их.
    """
    table_header = get_table_header(metadata, table_name)
    table_header.pop("ID")
    
    if len(values) != len(table_header):
        raise ValueError("Передано неверное количество значений")
    
    new_data = {}
    new_data['ID'] = max([i['ID'] for i in table_data], default=0) + 1
    for i, item in enumerate(table_header.items()):
        column_name, column_type = item
        column_value = values[i]
        
        if type(column_value).__name__ != column_type:
            raise ValueError(f'Неверный тип значения столбца "{column_name}"')
        new_data[column_name] = column_value
    
    table_data.append(new_data)
    return table_data

@decorators.log_time
@decorators.handle_db_errors
def select(table_data:list, where_clause:dict=None):
    """
    Если where_clause не задан, возвращает все данные.
    Если задан (например, {'age': 28}), фильтрует и возвращает только подходящие записи.
    """
    if where_clause is None or where_clause == {}:
        return table_data
    return [row for row in table_data if all([row.get(k) == v for k,v in where_clause.items()])]

@decorators.handle_db_errors
def update(table_data:list, set_clause:dict, where_clause:dict):
    """
    Находит записи по where_clause.
    Обновляет в найденных записях поля согласно set_clause.
    Возвращает измененные данные.
    """
    if not set_clause or not where_clause:
        raise ValueError("Для обновления нужны условия set и where")
    if "ID" in set_clause:
        raise ValueError("Изменение ID запрещено")
    data_to_update = select(table_data, where_clause)
    if data_to_update is None:
        return
    upd_table_data = [row.copy() for row in table_data]

    for row in upd_table_data:
        if row not in data_to_update:
            continue
        for k, v in set_clause.items():
            if type(row[k]) is not type(v):
                raise ValueError("Переданный тип не соответсвует типу колонки таблицы")
        row.update(set_clause)

    return upd_table_data

@decorators.confirm_action("удаление записи")
@decorators.handle_db_errors
def delete(table_data:list, where_clause:dict):
    """
    Находит записи по where_clause и удаляет их.
    Возвращает измененные данные.
    """
    if not where_clause:
        raise ValueError("Для удаления нужно условие where")
    data_to_delete = select(table_data, where_clause)
    if data_to_delete is None:
        return
    return [i for i in table_data if i not in data_to_delete]
