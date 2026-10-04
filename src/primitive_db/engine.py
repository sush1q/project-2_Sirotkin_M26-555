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
                try:
                    upd_metadata = core.create_table(actual_metadata, args[1], args[2:])
                    utils.save_metadata(db_file, upd_metadata)
                    # print(f'Таблица "{args[1]}" успешно создана со столбцами: {", ".join(args[2:])}')
                except (core.TableExistsError, core.TableArgumentsError) as e:
                    print(e)
                except:
                    print(f'Возникла ошибка при выполнении функции create_table с "{e}"')
                
            case "drop_table":
                try:
                    upd_metadata =  core.drop_table(actual_metadata, args[1])
                    utils.save_metadata(db_file, upd_metadata)
                    print(f'Таблица "{args[1]}" успешно удалена.')
                except (core.TableNotExistsError) as e:
                    print(e)
                except Exception as e:
                    print(f'Возникла ошибка при выполнении функции drop_table с типом "{e}"')

            case "list_tables":
                print(str("\n").join([f'- {table}' for table in actual_metadata.keys()]))
                
            case "insert":
                table_name, values = parser.parse_insert(args)
                table_data = utils.load_table_data(table_name)
                upd_table_data = core.insert(actual_metadata, table_name, table_data, values)
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
                table_data = utils.load_table_data(args[1])
                core.update(table_data, {}, {}) # TODO
            case "delete":
                table_data = utils.load_table_data(args[1])
                core.delete(table_data, {}) # TODO
            case "info":
                table_data = utils.load_table_data(args[1])
                
            case "help":
                print_help()
            case "exit":
                return
            case _:
                print(f"Функции {args[0]} нет. Попробуйте снова.")
