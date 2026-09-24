import shlex
import prompt
from . import core, utils


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
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
        
        args = shlex.split(user_input)

        match args[0]:
            case "create_table" | "drop_table" as cmd:
                try:
                    if cmd == "create_table":
                        upd_metadata = core.create_table(actual_metadata)
                    elif cmd == "drop_table":
                        upd_metadata =  core.drop_table(actual_metadata)

                    utils.save_metadata(db_file, upd_metadata)
                except:
                    print(f"Ошибка при выполнении функции {cmd}")
            case "list_tables":
                core.list_tables(actual_metadata)
            case "help":
                print_help()
            case "exit":
                return
            case _:
                print(f"Функции {args[0]} нет. Попробуйте снова.")
