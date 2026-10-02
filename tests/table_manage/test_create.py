import pytest
from src.primitive_db.core import *

def test_create_table():
    metadata = create_table({}, "test", ["ID:int"])
    assert metadata == {"test": {"ID": "int"}}


def test_create_table_adds_id_first_and_supports_all_types():
    result = create_table({}, "users", ["name:str", "age:int", "is_active:bool"])

    assert result == {
        "users": {"ID": "int", "name": "str", "age": "int", "is_active": "bool"}
    }
    assert list(result["users"]) == ["ID", "name", "age", "is_active"]


def test_explicit_id_is_not_duplicated_and_is_moved_to_start():
    result = create_table({}, "users", ["name:str", "ID:int", "age:int"])

    assert list(result["users"].items()) == [
        ("ID", "int"),
        ("name", "str"),
        ("age", "int"),
    ]


def test_create_table_preserves_other_tables():
    result = create_table({"products": {"ID": "int"}}, "users", ["name:str"])

    assert result == {
        "products": {"ID": "int"},
        "users": {"ID": "int", "name": "str"},
    }


def test_create_existing_table_does_not_overwrite_it():
    metadata = {"users": {"ID": "int", "name": "str"}}

    with pytest.raises(TableExistsError) as error:
        create_table(metadata, "users", ["age:int"])

    assert str(error.value) == 'Ошибка: Таблица "users" уже существует.'
    assert metadata == {"users": {"ID": "int", "name": "str"}}


@pytest.mark.parametrize("column_type", ["float", "integer", "list", "Int", ""])
def test_create_table_rejects_unsupported_types(column_type):
    metadata = {"products": {"ID": "int"}}

    with pytest.raises(TableArgumentsError):
        create_table(metadata, "users", ["name:str", f"age:{column_type}"])

    assert metadata == {"products": {"ID": "int"}}
