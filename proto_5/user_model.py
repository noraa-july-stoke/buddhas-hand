from typing import Any, Dict, List, Tuple, Union, Optional
from buddhas_hand_5 import BaseModel

from validations import is_string, is_email, is_not_email, name_length_check


class User(BaseModel):
    table_name: str = 'users'
    schema_name: str = 'buddhas_hand'

    def __init__(self, name: str, email: str, age: int, id: Optional[int] = id, **kwargs):
        super().__init__(id=id, name=name, email=email, age=age, **kwargs)

User.register_columns([
    {
        "name": "id",
        "type": "SERIAL PRIMARY KEY"
    },
    {
        "name": "name",
        "type": "TEXT",
        "validations": [is_string],
        "nullable": False,
    },
    {
        "name": "email",
        "type": "TEXT",
        "validations": [is_email],
        "nullable": False,
    },
    {
        "name": "age",
        "type": "INTEGER",
        "validations": [],
        "nullable": False,
    },
])







    # @classmethod
    # def register_columns(cls, **column_types: str):
    #     cls.column_types.update(column_types)
    #     cls.columns = list(column_types.keys())
