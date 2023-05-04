from buddhas_hand_6 import BaseModel, ForeignKey


class UserRole(BaseModel):
    table_name = "user_roles"
    schema_name = "buddhas_hand"

    @classmethod
    def register_columns(cls):
        super().register_columns([
            {
                "name": "user_id",
                "type": "INTEGER",
                "nullable": False,
                "foreign_key": ForeignKey(reference_table="users", reference_column="id", on_delete="CASCADE")
            },
            {
                "name": "role_id",
                "type": "INTEGER",
                "nullable": False,
                "foreign_key": ForeignKey(reference_table="roles", reference_column="id", on_delete="CASCADE")
            },
        ])
