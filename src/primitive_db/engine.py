import shlex
import prompt
import prettytable
from . import core, utils, parser


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

def run():
    """
    Загружайте актуальные метаданные с помощью load_metadata.
    Запрашивайте ввод у пользователя.
    Разбирайте введенную строку на команду и аргументы.
    Подсказка: Для надежного разбора строки используйте библиотеку shlex. args = shlex.split(user_input).
    Используйте if/elif/else или match/case для вызова соответствующей функции из core.py.
    После каждой успешной операции (create_table, drop_table) сохраняйте измененные метаданные с помощью save_metadata.
    """
    print("***База данных***")
    print_help()
    
    while True:
        db_file = "db_meta.json"
        actual_metadata = utils.load_metadata(db_file)
        user_input = prompt.string("Введите команду: ")
        
        args = shlex.split(user_input, posix=False)
        match args[0]:
            case "create_table":
                upd_metadata = core.create_table(actual_metadata, args[1], args[2:])
                if upd_metadata is not None:
                    utils.save_metadata(db_file, upd_metadata)
                    print(f'Таблица "{args[1]}" успешно создана со столбцами: {", ".join([f'{k}:{v}' for k,v in upd_metadata[args[1]].items()])}')

            case "drop_table":
                upd_metadata = core.drop_table(actual_metadata, args[1])
                if upd_metadata is not None:
                    utils.save_metadata(db_file, upd_metadata)
                    print(f'Таблица "{args[1]}" успешно удалена.')

            case "list_tables":
                print(str("\n").join([f'- {table}' for table in actual_metadata.keys()]))

            case "insert":
                table_name, values = parser.parse_insert(args)
                table_data = utils.load_table_data(table_name)
                upd_table_data = core.insert(actual_metadata, table_name, table_data, values)
                if upd_table_data is not None:
                    utils.save_table_data(table_name, upd_table_data)
                    
            case "select":
                table_name, clause = parser.parse_select(args)
                table_data = utils.load_table_data(table_name)
                selection = core.select(table_data, clause)
                
                table = prettytable.PrettyTable()
                if selection != []:
                    table.field_names = selection[0].keys()
                    table.add_rows([i.values() for i in selection])
                print(table)
                
            case "update":
                table_name, set_clause, where_clause = parser.parse_update(args)
                table_data = utils.load_table_data(table_name)
                upd_table_data = core.update(table_data, set_clause, where_clause)
                if upd_table_data is not None:
                    utils.save_table_data(table_name, upd_table_data)

            case "delete":
                table_name, where_clause = parser.parse_delete(args)
                table_data = utils.load_table_data(table_name)
                upd_table_data = core.delete(table_data, where_clause)
                if upd_table_data is not None:
                    utils.save_table_data(table_name, upd_table_data)

            case "info":
                table_data = utils.load_table_data(args[1])
                print(f"Таблица: {args[1]}\n"\
                    f"Столбцы: {", ".join([f"{k}:{v}" for k, v in actual_metadata[args[1]].items()])}\n"\
                    f"Количество записей: {len(table_data)}\n"
                )

            case "help":
                print_help()
            case "exit":
                return 0
            case _:
                print(f"Функции {args[0]} нет. Попробуйте снова.")
