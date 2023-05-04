from buddhas_hand_6 import BaseModel, ForeignKey
# from proto_6 import UserRole


class UserRole(BaseModel):
    schema_name = "buddhas_hand"
    table_name = "user_roles"


columns = [
        {
            "name": "user_id",
            "type": "INTEGER",
            "foreign_key": ForeignKey(
                reference_table="users",
                reference_column="id",
                on_delete="CASCADE",
            ),
        },
        {
            "name": "role_id",
            "type": "INTEGER",
            "foreign_key": ForeignKey(
                reference_table="roles",
                reference_column="id",
                on_delete="CASCADE",
            ),
        },
    ]

UserRole.register_columns(columns)
