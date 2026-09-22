import prompt


def welcome():
    prompt_str = "<command> exit - выйти из программы\n"\
                "<command> help - справочная информация\n"\
                "Введите команду: "
    prompt.string(prompt_str)

