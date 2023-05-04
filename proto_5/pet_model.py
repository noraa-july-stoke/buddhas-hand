from typing import Optional
from buddhas_hand_5 import BaseModel
from validations import is_string


class Pet(BaseModel):
    table_name: str = 'pets'
    schema_name: str = 'buddhas_hand'

    def __init__(self, name: str, species: str, owner_id: int, id: Optional[int] = None, **kwargs):
        super().__init__(id=id, name=name, species=species, owner_id=owner_id, **kwargs)


Pet.register_columns([
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
