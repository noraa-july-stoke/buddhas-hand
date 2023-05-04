from buddhas_hand_6 import BaseModel
from user_role import UserRole

class Role(BaseModel):
    table_name = "roles"
    schema_name = "buddhas_hand"

    relations = {
        "User": {
            "assoc_table": UserRole,
            "foreign_key": "role_id",
            "reference_key": "user_id",
        }
    }

    @classmethod
    def register_columns(cls):
        super().register_columns([
            {
                "name": "name",
                "type": "VARCHAR",
                "nullable": False,
            },
        ])
