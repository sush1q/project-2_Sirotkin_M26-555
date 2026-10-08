from . import constants, decorators


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
    """Проверяет схему и возвращает метаданные с новой таблицей и столбцом ID."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    table_data = {constants.ID_COLUMN: constants.ID_TYPE}
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
        if column_name == constants.ID_COLUMN and column_type != constants.ID_TYPE:
            raise ValueError("Столбец ID должен иметь тип int")
        seen_columns.add(column_name)
        table_data[column_name] = column_type
    
    upd_metadata = metadata.copy()
    upd_metadata[table_name] = table_data
    return upd_metadata

@decorators.confirm_action("удаление таблицы")
@decorators.handle_db_errors
def drop_table(metadata: dict, table_name: str):
    """Возвращает метаданные без указанной таблицы после проверки её наличия."""
    get_table_header(metadata, table_name)
    upd_metadata = metadata.copy()
    upd_metadata.pop(table_name)
    return upd_metadata

@decorators.log_time
@decorators.handle_db_errors
def insert(metadata:dict, table_name:str, table_data:list, values:list):
    """Проверяет значения, добавляет запись с новым ID и возвращает данные."""
    table_header = get_table_header(metadata, table_name)
    table_header.pop(constants.ID_COLUMN)
    
    if len(values) != len(table_header):
        raise ValueError("Передано неверное количество значений")
    
    new_data = {}
    new_data[constants.ID_COLUMN] = max(
        [i[constants.ID_COLUMN] for i in table_data], default=0
    ) + 1
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
    """Возвращает все записи или записи, подходящие под условие where."""
    if where_clause is None or where_clause == {}:
        return table_data
    return [
        row for row in table_data
        if all([row.get(k) == v for k,v in where_clause.items()])
    ]

@decorators.handle_db_errors
def update(table_data:list, set_clause:dict, where_clause:dict):
    """Обновляет поля подходящих записей и возвращает изменённые данные."""
    if not set_clause or not where_clause:
        raise ValueError("Для обновления нужны условия set и where")
    if constants.ID_COLUMN in set_clause:
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
    """Возвращает данные без записей, подходящих под условие where."""
    if not where_clause:
        raise ValueError("Для удаления нужно условие where")
    data_to_delete = select(table_data, where_clause)
    if data_to_delete is None:
        return
    return [i for i in table_data if i not in data_to_delete]
