from typing import List, Optional
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


class BaseModel:
    table_name = None
    schema_name = None

    def __init__(self, id: Optional[int] = None):
        self.id = id

    def delete(self, cur, conn):
        query = f"DELETE FROM {self.schema_name}.{self.table_name} WHERE id = %s;"
        cur.execute(query, (self.id,))
        conn.commit()


class User(BaseModel):
    table_name = 'users'
    schema_name = 'buddhas_hand'

    def __init__(self, name: str, email: str, id: Optional[int] = None):
        super().__init__(id=id)
        self.name = name
        self.email = email

    def insert(self, cur, conn):
        query = f'''
            INSERT INTO {self.schema_name}.{self.table_name} (name, email)
            VALUES (%s, %s)
            RETURNING id;
        '''
        cur.execute(query, (self.name, self.email))
        result = cur.fetchone()
        self.id = result[0]  # change this line
        conn.commit()

    def update(self, cur, conn):
        query = f'''
            UPDATE {self.schema_name}.{self.table_name}
            SET name = %s, email = %s
            WHERE id = %s;
        '''
        cur.execute(query, (self.name, self.email, self.id))
        conn.commit()

    @classmethod
    def find_all(cls, cur, **kwargs):
        # Build the WHERE clause dynamically based on the kwargs
        # and their corresponding column names
        where_clause = " AND ".join(f"{k} = %s" for k in kwargs.keys())
        values = tuple(kwargs.values())

        query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE {where_clause};"
        cur.execute(query, values)
        results = cur.fetchall()
        return [cls(**row) for row in results]

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

    def save(self, cur, conn):
        if self.id:
            self.update(cur, conn)
        else:
            self.insert(cur, conn)
