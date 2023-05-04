from typing import Optional
from buddhas_hand_5 import BaseModel
from validations import is_string


class Pet(BaseModel):
    table_name: str = 'pets'
    schema_name: str = 'buddhas_hand'
    relations = {
        "User": {
            'foreign_key': 'owner_id',
            'reference_key': 'id'
        }
    }

    def __init__(self, name: str, species: str, owner_id: int, **kwargs):
        super().__init__(name=name, species=species, owner_id=owner_id, **kwargs)


Pet.register_columns([
    {
        "name": "name",
        "type": "TEXT",
        "validations": [is_string],
        "nullable": False,
    },
    {
        "name": "species",
        "type": "TEXT",
        "validations": [is_string],
        "nullable": False,
    },
    {
        "name": "owner_id",
        "type": "INTEGER",
        "validations": [],
        "nullable": False,
        "foreign_key": {
            "reference_table": "users",
            "reference_column": "id",
            "on_delete": "CASCADE",
        },
    },
])
