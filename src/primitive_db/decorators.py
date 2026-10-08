import time
import prompt


def handle_db_errors(func):
    """Перехватывает ошибки операции и выводит сообщение пользователю."""
    def wrapper(*args, **kwargs):
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
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

def confirm_action(action_name):
    """Запрашивает подтверждение перед выполнением указанного действия."""
    def wrapper(func):
        def real_wrapper(*args, **kwargs):
            user_input = prompt.string(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ', empty=True)
            if user_input.lower() != 'y':
                return
            return func(*args, **kwargs)
        real_wrapper.__name__ = func.__name__
        real_wrapper.__doc__ = func.__doc__
        return real_wrapper
    return wrapper

def log_time(func):
    """Выводит время выполнения функции и возвращает её результат."""
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        ret = func(*args, **kwargs)
        finish = time.monotonic()
        
        print(f'Функция {func.__name__} выполнилась за {finish - start:.3f} секунд')
        return ret
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__   
    return wrapper

def create_cacher():
    """Возвращает функцию, хранящую результаты вычислений в замыкании."""
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        cache[key] = value_func()
        return cache[key] 
    return cache_result
