
# insert into users values ( "Sergei A" , 28 , true )
# insert into users values ( 'Sergei B', 30, false  )
def parse_insert(command:list):
    values = "".join(command[4:])

    if command[0] != "insert" or command[1] != "into" or command[3] != "values" or values[0] != "(" or values[-1] != ")":
        raise ValueError("Переданная команда не соответсвует формату insert")

    table_name = command[2]
    return (table_name, values[1:-1].split(","))

# select from users where age = 28
# select from users
def parse_select(command: list):
    should_be_clause = len(command) > 3
    
    if command[0] != 'select' or command[1] != 'from' or (should_be_clause and (len(command) not in [3,7] or command[3] != 'where' or command[5] != '=')):
        raise ValueError("Переданная команда не соответсвует формату select")
    
    table_name = command[2]
    clause = None
    if should_be_clause:
        clause = {}
        clause[command[4]] = command[6]
    
    return (table_name, clause)

# update users set age = 29 where name = "Sergei"
def parse_update(command:list):
    if command[0] != 'update' or command[2] != 'set' or command[6] != 'where' or command[4] != '=' or command[8] != '=':
        raise ValueError("Переданная команда не соответсвует формату update")

    table_name = command[1]
    set_clause = {command[3]: command[5]}
    where_clause = {command[7]: command[9]}
    
    return (table_name, set_clause, where_clause)

# delete from users where ID = 1
def parse_delete(command:list):
    if command[0] != 'delete' or command[1] != 'from' or command[3] != 'where' or command[5] != '=':
        raise ValueError("Переданная команда не соответсвует формату delete")
    table_name = command[1]
    where_clause = {command[4]: command[6]}
    
    return (table_name, where_clause)
