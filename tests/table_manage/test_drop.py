import pytest
from src.primitive_db.core import TableNotExistsError, drop_table


def test_drop_table_preserves_other_tables():
    metadata = {"users": {"ID": "int"}, "products": {"ID": "int", "name": "str"}}

    result = drop_table(metadata, "users")

    assert result == {"products": {"ID": "int", "name": "str"}}


def test_drop_last_table_returns_empty_metadata():
    assert drop_table({"users": {"ID": "int"}}, "users") == {}


@pytest.mark.parametrize("metadata", [{}, {"users": {"ID": "int"}}])
def test_drop_missing_table_preserves_metadata(metadata):
    before = {name: columns.copy() for name, columns in metadata.items()}

    with pytest.raises(TableNotExistsError) as error:
        drop_table(metadata, "products")

    assert str(error.value) == 'Ошибка: Таблица "products" не существует.'
    assert metadata == before
