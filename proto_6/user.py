from typing import TYPE_CHECKING
from buddhas_hand_6 import BaseModel
from user_role import UserRole
from role import Role

class User(BaseModel):
    table_name = "users"
    schema_name = "buddhas_hand"
    relations = {
        Role: {
            'assoc_table': UserRole,
            'foreign_key': 'user_id',
            'reference_key': 'role_id'
        }
    }

columns = [
        {
            "name": "username",
            "type": "VARCHAR",
            "nullable": False,
        },
        {
            "name": "email",
            "type": "VARCHAR",
            "nullable": False,
        },
    ]

User.register_columns(columns)
