import prompt
from functools import wraps


def handle_db_errors(func):
    """
    Создайте декоратор, который оборачивает вызов функции в блок try...except.
    Он должен перехватывать как минимум KeyError (например, обращение к несуществующей таблице), ValueError (ошибки валидации типов) и FileNotFoundError.
    Примените этот декоратор ко всем функциям в db_core, которые могут вызвать эти исключения. Теперь вам не нужно писать try...except в каждой из них.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: либо удалить свои эксепшнены, либо расширить логику тут
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper

def confirm_action(action_name):
    def wrapper(func):
        @wraps(func)
        def real_wrapper(*args, **kwargs):
            user_input = prompt.string(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if user_input.lower() != 'y':
                return
            return func(args, kwargs)
        real_wrapper
    return wrapper
