import shlex


def tokenize(command:str):
    """Разбивает команду на аргументы, сохраняя кавычки."""
    separators = "(),="
    lexer = shlex.shlex(
        command,
        posix=False,
        punctuation_chars=separators,
    )
    lexer.whitespace_split = True
    lexer.commenters = ""

    tokens = []
    for token in lexer:
        if token[0] in separators:
            tokens.extend(token)
        else:
            tokens.append(token)

    return tokens

def parse_value(value:str):
    """Преобразует значение команды в int, str или bool."""
    if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
        return value[1:-1]

    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    try:
        return int(value)
    except ValueError:
        raise ValueError(f'Некорректное значение: {value}. Строки должны быть в кавычках.')

def parse_clause(command:list):
    """Разбирает одно условие вида столбец = значение."""
    if len(command) != 3 or command[1] != "=":
        raise ValueError("Условие должно иметь вид: столбец = значение")
    return {command[0]: parse_value(command[2])}


def parse_insert(command:list):
    if len(command) < 6 or command[:2] != ["insert", "into"] or command[3:5] != ["values", "("] or command[-1] != ")":
        raise ValueError("Переданная команда не соответствует формату insert")

    values = command[5:-1]
    if any(value != "," for value in values[1::2]):
        raise ValueError("Между значениями должна быть запятая")
    return (command[2], [parse_value(value) for value in values[::2]])

def parse_select(command:list):
    if len(command) not in [3, 7] or command[:2] != ["select", "from"]:
        raise ValueError("Переданная команда не соответствует формату select")
    clause = None
    if len(command) == 7:
        if command[3] != "where":
            raise ValueError("Переданная команда не соответствует формату select")
        clause = parse_clause(command[4:])
    return (command[2], clause)

def parse_update(command:list):
    if len(command) != 10 or command[0] != "update" or command[2] != "set" or command[6] != "where":
        raise ValueError("Переданная команда не соответствует формату update")

    table_name = command[1]
    set_clause = parse_clause(command[3:6])
    where_clause = parse_clause(command[7:])

    return (table_name, set_clause, where_clause)

def parse_delete(command:list):
    if len(command) != 7 or command[:2] != ["delete", "from"] or command[3] != "where":
        raise ValueError("Переданная команда не соответствует формату delete")
    return (command[2], parse_clause(command[4:]))
