from typing import TYPE_CHECKING
from buddhas_hand_6 import BaseModel
from user_role import UserRole
from user import User

class Role(BaseModel):
    table_name = "roles"
    schema_name = "buddhas_hand"
    relations = {
        User: {
            "assoc_table": UserRole,
            "foreign_key": "role_id",
            "reference_key": "user_id",
        }
    }

columns = [
        {
            "name": "name",
            "type": "VARCHAR",
            "nullable": False,
        },
    ]

Role.register_columns(columns)
