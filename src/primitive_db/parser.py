
def parse_insert(command:list):
    values = "".join(command[4:])

    if command[0] != "insert" or command[1] != "into" or command[3] != "values" or values[0] != "(" or values[-1] != ")":
        raise ValueError("Переданная команда не соответсвует формату insert")

    table_name = command[2]
    return (table_name, values[1:-1].split(","))


# insert into users values ( "Sergei A" , 28 , true )