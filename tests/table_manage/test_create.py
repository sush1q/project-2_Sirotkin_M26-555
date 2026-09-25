import pytest
from src.primitive_db.core import *

def test_create_table():
    metadata = create_table({},"test",["ID:int"])
    assert metadata == {"test": {"ID": "int"}}

