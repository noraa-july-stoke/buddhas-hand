from buddhas_hand_6 import BaseModel
from user_role import UserRole

class User(BaseModel):
    table_name = "users"
    schema_name = "buddhas_hand"
    relations = {
        UserRole: {
            'assoc_table': UserRole,
            'foreign_key': 'user_id',
            'reference_key': 'role_id'
        }
    }

    @classmethod
    def register_columns(cls):
        super().register_columns([
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
        ])
