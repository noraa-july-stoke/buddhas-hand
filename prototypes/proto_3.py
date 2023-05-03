from typing import Any, Dict, List, Tuple, Union, Optional
import psycopg2
import psycopg2.extensions


class Database:
    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string

    def create_schema(self, schema_name: str) -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
                conn.commit()

    def create_table(self, table: 'Table') -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:

                columns_str = ", ".join(f"{col.name} {col.data_type}" for col in table.columns)

                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table.schema_name}.{table.name} (
                        id SERIAL PRIMARY KEY,
                        {columns_str}
                    );
                """)
                conn.commit()


    def drop_schema(self, schema_name: str) -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
                conn.commit()

    def drop_table(self, table_name: str, schema_name: str) -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name};")
                conn.commit()


class Column:
    def __init__(self, name: str, data_type: str):
        self.name = name
        self.data_type = data_type


class Table:
    def __init__(self, name: str, schema_name: str, columns: List[Column]):
        self.name = name
        self.schema_name = schema_name
        self.columns = columns

    @classmethod
    def from_model(cls, model):
        columns = [Column(name, data_type) for name, data_type in model.column_types.items()]
        return cls(model.table_name, model.schema_name, columns)


class BaseModel:
    table_name = None
    schema_name = None
    columns = []

    def __init__(self, id: Optional[int] = None, **kwargs):
        self.id = id
        for column in self.columns:
            setattr(self, column, kwargs.get(column))

    @classmethod
    def register_columns(cls, *column_names: str):
        cls.columns.extend(column_names)

    def _insert_values(self) -> Tuple[str, List[Union[str, int]]]:
        columns = []
        values = []
        for column, data_type in self.column_types.items():
            columns.append(column)
            values.append(getattr(self, column))
        return ", ".join(columns), values


    def insert(self, cur, conn):
        columns_str, values = self._insert_values()
        query = f'''
            INSERT INTO {self.schema_name}.{self.table_name} ({columns_str})
            VALUES ({", ".join(["%s"] * len(values))})
            RETURNING id;
        '''
        cur.execute(query, values)
        result = cur.fetchone()
        self.id = result[0]
        conn.commit()

    def update(self, cur, conn):
        update_columns = ", ".join(f"{column} = %s" for column in self.columns)
        query = f'''
            UPDATE {self.schema_name}.{self.table_name}
            SET {update_columns}
            WHERE id = %s;
        '''
        values = [getattr(self, column) for column in self.columns] + [self.id]
        cur.execute(query, values)
        conn.commit()

    def delete(self, cur, conn):
        query = f"DELETE FROM {self.schema_name}.{self.table_name} WHERE id = %s;"
        cur.execute(query, (self.id,))
        conn.commit()

    @classmethod
    def find_all(cls, cur, **kwargs):
        if kwargs:
            # Build the WHERE clause dynamically based on the kwargs
            # and their corresponding column names
            where_clause = " AND ".join(f"{k} = %s" for k in kwargs.keys())
            values = tuple(kwargs.values())

            query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE {where_clause};"
            cur.execute(query, values)
        else:
            query = f"SELECT * FROM {cls.schema_name}.{cls.table_name};"
            cur.execute(query)

        results = cur.fetchall()

        # Convert the tuples into dictionaries
        column_names = [desc[0] for desc in cur.description]
        results_as_dicts = [dict(zip(column_names, row)) for row in results]

        return [cls(**row) for row in results_as_dicts]

    @classmethod
    def get_by_id(cls, cur, id):
        query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE id = %s;"
        cur.execute(query, (id,))
        result = cur.fetchone()
        if result:
            result_dict = {
                'id': result[0],
                'name': result[1],
                'email': result[2]
            }
            return cls(**result_dict)
        return None


class User(BaseModel):
    table_name = 'users'
    schema_name = 'buddhas_hand'
    column_types = {}

    def __init__(self, name: str, email: str, age: int, id: Optional[int] = None):
        super().__init__(id=id, name=name, email=email, age=age)

    @classmethod
    def register_columns(cls, **column_types: str):
        cls.column_types.update(column_types)
        cls.columns = list(column_types.keys())
