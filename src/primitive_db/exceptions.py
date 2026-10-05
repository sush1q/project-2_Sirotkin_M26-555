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

class ArgumentError(Exception):
    def __init__(self, arg):
        self.arg = arg
    def __str__(self):
        return f'Некорректное значение: {self.arg}. Попробуйте снова.'
