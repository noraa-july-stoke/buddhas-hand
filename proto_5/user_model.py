from typing import Any, Dict, List, Tuple, Union, Optional
from buddhas_hand_5 import BaseModel
# from pydantic import BaseModel, EmailStr, validator

class User(BaseModel):
    table_name: str = 'users'
    schema_name: str = 'buddhas_hand'

    def __init__(self, name: str, email: str, age: int, id: Optional[int] = None, **kwargs):
        super().__init__(id=id, name=name, email=email, age=age, **kwargs)

    # @classmethod
    # def register_columns(cls, **column_types: str):
    #     cls.column_types.update(column_types)
    #     cls.columns = list(column_types.keys())
