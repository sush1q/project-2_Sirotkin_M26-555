
# insert into users values ( "Sergei A" , 28 , true )
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
    clause = {}
    if should_be_clause:
        clause[command[4]] = command[6]
    
    return (table_name, clause)
