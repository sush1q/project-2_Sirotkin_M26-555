import prompt
import prettytable
from . import core, utils, parser, constants, decorators


def print_help():
    """Prints the help message for the current mode."""
   
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

@decorators.handle_db_errors
def execute_command(user_input:str):
    """Разбирает и выполняет команду; возвращает 0 для выхода из программы."""
    args = parser.tokenize(user_input)
    if not args:
        return
    if args[0] in ["help", "exit", "list_tables"] and len(args) != 1:
        raise ValueError("Команда не принимает аргументы")
    if args[0] in ["drop_table", "info"] and len(args) != 2:
        raise ValueError("Укажите имя таблицы")
    if args[0] == "create_table" and len(args) < 3:
        raise ValueError("Укажите имя таблицы и столбцы")

    if args[0] == "exit":
        return 0
    if args[0] == "help":
        print_help()
        return

    actual_metadata = utils.load_metadata(constants.META_FILE)
    match args[0]:
        case "create_table":
            upd_metadata = core.create_table(actual_metadata, args[1], args[2:])
            if upd_metadata is not None:
                utils.save_metadata(constants.META_FILE, upd_metadata)
                print(f'Таблица "{args[1]}" успешно создана со столбцами: {", ".join([f'{k}:{v}' for k,v in upd_metadata[args[1]].items()])}')

        case "drop_table":
            upd_metadata = core.drop_table(actual_metadata, args[1])
            if upd_metadata is not None:
                utils.delete_table(args[1])
                utils.save_metadata(constants.META_FILE, upd_metadata)
                print(f'Таблица "{args[1]}" успешно удалена.')

        case "list_tables":
            print(str("\n").join([f'- {table}' for table in actual_metadata.keys()]))

        case "insert":
            table_name, values = parser.parse_insert(args)
            table_data = utils.load_table_data(table_name)
            upd_table_data = core.insert(actual_metadata, table_name, table_data, values)
            if upd_table_data is not None:
                utils.save_table_data(table_name, upd_table_data)
                row_id = upd_table_data[-1][constants.ID_COLUMN]
                print(f'Запись с ID={row_id} успешно добавлена в таблицу "{table_name}".')

        case "select":
            table_name, clause = parser.parse_select(args)
            table_header = core.get_table_header(actual_metadata, table_name)
            core.check_clause(table_header, clause)
            table_data = utils.load_table_data(table_name)
            selection = core.select(table_data, clause)
            if selection is not None:
                table = prettytable.PrettyTable()
                table.field_names = table_header.keys()
                table.add_rows(
                    [[row[column] for column in table_header] for row in selection]
                )
                print(table)

        case "update":
            table_name, set_clause, where_clause = parser.parse_update(args)
            table_header = core.get_table_header(actual_metadata, table_name)
            core.check_clause(table_header, set_clause)
            core.check_clause(table_header, where_clause)
            table_data = utils.load_table_data(table_name)
            upd_table_data = core.update(table_data, set_clause, where_clause)
            if upd_table_data is not None:
                utils.save_table_data(table_name, upd_table_data)
                for row in table_data:
                    if all(row.get(k) == v for k, v in where_clause.items()):
                        row_id = row[constants.ID_COLUMN]
                        print(f'Запись с ID={row_id} в таблице "{table_name}" успешно обновлена.')

        case "delete":
            table_name, where_clause = parser.parse_delete(args)
            table_header = core.get_table_header(actual_metadata, table_name)
            core.check_clause(table_header, where_clause)
            table_data = utils.load_table_data(table_name)
            upd_table_data = core.delete(table_data, where_clause)
            if upd_table_data is not None:
                utils.save_table_data(table_name, upd_table_data)
                for row in table_data:
                    if row not in upd_table_data:
                        row_id = row[constants.ID_COLUMN]
                        print(f'Запись с ID={row_id} успешно удалена из таблицы "{table_name}".')

        case "info":
            table_header = core.get_table_header(actual_metadata, args[1])
            table_data = utils.load_table_data(args[1])
            print(f"Таблица: {args[1]}\n"\
                f"Столбцы: {", ".join([f"{k}:{v}" for k, v in table_header.items()])}\n"\
                f"Количество записей: {len(table_data)}\n"
            )

        case _:
            print(f"Функции {args[0]} нет. Попробуйте снова.")


def run():
    """Принимает команды до exit, конца ввода или прерывания пользователем."""
    print_help()

    while True:
        try:
            user_input = prompt.string("Введите команду: ", empty=True)
            if execute_command(user_input or "") == 0:
                return 0
        except (EOFError, KeyboardInterrupt):
            return 0
